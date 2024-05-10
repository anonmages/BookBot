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

  private findSessionByUserId(userId: string): ChatSession | undefined {
    return this.sessions.find(session => session.userId === userId && (Date.now() - session.lastActivity) < this.sessionTimeout);
  }

  private createSession(userId: string): ChatSession {
    const newSession: ChatSession = {
      userId: userId,
      sessionId: uuidv4(),
      messages: [],
      lastActivity: Date.now(),
    };
    this.sessions.push(newSession);
    return newSession;
  }

  public getSession(userId: string): ChatSession {
    let session = this.findSessionByUserId(userId);

    if (!session) {
      session = this.createSession(userId);
    } else {
      session.lastActivity = Date.now();
    }

    return session;
  }

  public addMessageToSession(userId: string, message: string): void {
    const session = this.getSession(userId);
    session.messages.push(message);
  }

  public cleanUpSessions(): void {
    const currentTime = Date.now();
    this.sessions = this.sessions.filter(session => (currentTime - session.lastActivity) < this.sessionTimeout);
  }
}
