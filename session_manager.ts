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
    this.sessionIdleLimit = parseInt(process.env.SESSION_TIMEOUT || "1800000");
  }

  private isSessionCurrentlyActive(session: ChatSession): boolean {
    return (Date.now() - session.lastInteractionTime) < this.sessionIdleLimit;
  }

  private getSessionByUserId(userId: string): ChatSession | undefined {
    return this.activeSessions.find(session => session.userId === userId && this.isSessionCurrentlyActive(session));
  }

  private createNewSession(userId: string): ChatSession {
    const newSession = this.initializeNewSession(userId);
    this.activeSessions.push(newSession);
    return newSession;
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
    session.lastInteractionTime = Date.now();
  }

  public fetchOrCreateSession(userId: string): ChatSession {
    let session = this.getSessionByUserId(userId);

    if (!session) {
      session = this.createNewSession(userId);
    } else {
      this.refreshSessionActivity(session);
    }

    return session;
  }

  public logMessageInSession(userId: string, message: string): void {
    const session = this.fetchOrCreateSession(userId);
    this.recordMessageInSession(session, message);
  }

  private recordMessageInSession(session: ChatSession, message: string): void {
    session.messages.push(message);
  }

  public purgeInactiveSessions(): void {
    this.activeSessions = this.activeSessions.filter(session => this.isSessionCurrentlyActive(session));
  }
}

const sessionManager = new SessionManager();
sessionManager.logMessageInSession("user1", "Hello, how can I assist you?");
console.log(sessionManager.activeSessions);