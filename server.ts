import express, { Request, Response, NextFunction } from 'express';
import bodyParser from 'body-parser';
import session from 'express-session';
import dotenv from 'dotenv';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

const logFilePath = path.join(__dirname, 'bookBotLog.txt');
const logStream = fs.createWriteStream(logFilePath, { flags: 'a' });

const log = (message: string): void => {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  logStream.write(logMessage);
  console.log(logMessage);
};

app.use(bodyParser.json());
app.use(session({
  secret: process.env.SESSION_SECRET || 'default_secret',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: !process.env.DEBUG },
}));

const callPythonChatbot = async (text: string, sessionId: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['path/to/python_script.py', text, sessionId]);

    let dataChunks: Buffer[] = [];
    pythonProcess.stdout.on('data', (data: Buffer) => {
      dataChunks.push(data);
    });

    pythonProcess.stdout.on('end', () => {
      const output = Buffer.concat(dataChunks).toString();
      log(`Python Output: ${output}`);
      resolve(output);
    });

    pythonProcess.stderr.on('data', (data) => {
      log(`stderr: ${data}`);
      console.error(`stderr: ${data}`);
    });

    pythonProcess.on('error', (error) => {
      log(`Failed to start subprocess: ${error}`);
      console.error(`Failed to start subprocess: ${error}`);
      reject(new Error('Failed to start subprocess'));
    });

    pythonProcess.on('close', (code) => {
      log(`Python script exited with code ${code}`);
      if (code !== 0) {
        console.log(`Python script exited with code ${code}`);
        reject(new Error('Python script exited with an error'));
      }
    });
  });
};

app.post('/message', async (req: Request, res: Response, next: NextFunction) => {
  const { message } = req.body;
  log(`Received message: ${message}`);
  if (typeof message !== 'string' || message.trim() === '') {
    return res.status(400).send('Invalid input: Please provide a non-empty message string.');
  }

  const sessionId = req.sessionID;

  try {
    const chatbotResponse = await callPythonChatbot(message, sessionId);
    res.json({ message: chatbotResponse });
  } catch (error) {
    next(error);
  }
});

app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  log(`Error: ${err.stack}`);
  console.error(err.stack);
  if (res.headersSent) {
    return next(err);
  }
  const statusCode = err.statusCode || 500;
  const errorMessage = err.message || 'Internal Server Error';
  res.status(statusCode).send(errorMessage);
});

app.listen(PORT, () => {
  log(`Server running on port ${PORT}`);
  console.log(`Server running on port ${PORT}`);
});