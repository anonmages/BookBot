import * as dotenv from "dotenv";
import { v4 as uuidv4 } from "uuid";

dotenv.config();

interface ChatSession {
  userId: string;
  sessionId: string;
  messages: Array<string>;
  lastActivity: number; 
}

class ChatSessionManager {
  sessions: ChatSession[] = [];
  sessionTimeout: number;

  constructor() {
    this.sessionTimeout = parseInt(process.env.SESSION_TIMEOUT || "1800000");
  }

  private isSessionActive(session: ChatSession): boolean {
    return (Date.now() - session.lastActivity) < this.sessionTimeout;
  }

  private findSessionByUserId(userId: string): ChatSession | undefined {
    return this.sessions.find(session => session.userId === userId && this.isSessionActive(session));
  }

  private createSession(userId: string): ChatSession {
    const newSession = this.initializeSession(userId);
    this.sessions.push(newSession);
    return newSession;
  }

  private initializeSession(userId: string): ChatSession {
    return {
      userId: userId,
      sessionId: uuidv4(),
      messages: [],
      lastActivity: Date.now(),
    };
  }

  private updateSessionActivity(session: ChatSession): void {
    session.lastActivity = Date.now();
  }

  public getSession(userId: string): ChatSession {
    let session = this.findSessionByUserId(userId);

    if (!session) {
      session = this.createSession(userId);
    } else {
      this.updateSessionActivity(session);
    }

    return session;
  }

  public addMessageToSession(userId: string, message: string): void {
    const session = this.getSession(userId);
    this.appendMessageToSession(session, message);
  }

  private appendMessageToSession(session: ChatSession, message: string): void {
    session.messages.push(message);
  }

  public cleanUpSessions(): void {
    this.sessions = this.sessions.filter(session => this.isSessionActive(session));
  }
}

// Example usage
const chatSessionManager = new ChatSessionManager();
chatSessionManager.addMessageToSession("user1", "Hello, how can I assist you?");
console.log(chatSessionManager.sessions);