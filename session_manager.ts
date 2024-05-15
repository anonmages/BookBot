import * as dotenv from "dotenv";
import { v4 as uuidv4 } from "uuid";

dotenv.config();

interface ChatSession {
  userId: string;
  sessionId: string;
  messages: Array<string>;
  lastInteractionTime: number; 
}

class SessionManager {
  activeSessions: ChatSession[] = [];
  sessionIdleLimit: number;

  constructor() {
    this.sessionIdleLimit = this.parseSessionTimeout(process.env.SESSION_TIMEOUT);
  }

  private parseSessionTimeout(timeout: string | undefined): number {
    try {
      const parsedTimeout = parseInt(timeout || "1800000", 10);
      if (isNaN(parsedTimeout)) {
        throw new Error("SESSION_TIMEOUT is not a valid number");
      }
      return parsedTimeout;
    } catch(error) {
      console.error("Error parsing SESSION_TIMEOUT from environment variables", error);
      return 1800000; 
    }
  }

  private isSessionCurrentlyActive(session: ChatSession): boolean {
    return (Date.now() - session.lastInteractionTime) < this.sessionIdleLimit;
  }

  private getSessionByUserId(userId: string): ChatSession | undefined {
    try {
      return this.activeSessions.find(session => session.userId === userId && this.isSessionCurrentlyActive(session));
    } catch(error) {
      console.error("Error fetching session by user ID", error);
      return undefined;
    }
  }

  private createNewSession(userId: string): ChatSession {
    try {
      const newSession = this.initializeNewSession(userId);
      this.activeSessions.push(newSession);
      return newSession;
    } catch(error) {
      console.error("Error creating new session", error);
      throw error;
    }
  }

  private initializeNewSession(userId: string): ChatSession {
    return {
      userId: userId,
      sessionId: uuidv4(),
      messages: [],
      lastInteractionTime: Date.now(),
    };
  }

  private refreshSessionActivity(session: ChatSession): void {
    try {
      session.lastInteractionTime = Date.now();
    } catch(error) {
      console.error("Error refreshing session activity", error);
    }
  }

  public fetchOrCreateSession(userId: string): ChatSession {
    try {
      let session = this.getSessionByUserId(userId);

      if (!session) {
        session = this.createNewSession(userId);
      } else {
        this.refreshSessionActivity(session);
      }

      return session;
    } catch(error) {
      console.error("Error fetching or creating a session", error);
      throw error;
    }
  }

  public logMessageInSession(userId: string, message: string): void {
    try {
      const session = this.fetchOrCreateSession(userId);
      this.recordMessageInSession(session, message);
    } catch(error) {
      console.error("Error logging message in session", error);
    }
  }

  private recordMessageInSession(session: ChatSession, message: string): void {
    try {
      session.messages.push(message);
    } catch(error) {
      console.error("Error recording message in session", error);
    }
  }

  public purgeInactiveSessions(): void {
    try {
      this.activeSessions = this.activeSessions.filter(session => this.isSessionCurrentlyActive(session));
    } catch(error) {
      console.error("Error purging inactive sessions", error);
    }
  }
}

const sessionManager = new SessionManager();
try {
    sessionManager.logMessageInSession("user1", "Hello, how can I assist you?");
    console.log(sessionManager.activeSessions);
} catch (error) {
    console.error("An error occurred during session management", error);
}