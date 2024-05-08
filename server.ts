import express, { Request, Response } from 'express';
import bodyParser from 'body-parser';
import session from 'express-session';
import dotenv from 'dotenv';
import { spawn } from 'child_process';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

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

    pythonProcess.stdout.on('data', (data) => {
      resolve(data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
      reject(new Error('Error in Python script processing'));
    });

    pythonProcess.on('error', (error) => {
      console.error(`Failed to start subprocess: ${error}`);
      reject(new Error('Failed to start subprocess'));
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.log(`Python script exited with code ${code}`);
        reject(new Error('Python script exited with an error'));
      }
    });
  });
};

app.post('/message', async (req: Request, res: Response) => {
  const { message } = req.body;
  if (typeof message !== 'string' || message.trim() === '') {
    return res.status(400).send('Invalid input: Please provide a non-empty message string.');
  }

  const sessionId = req.sessionID;

  try {
    const chatbotResponse = await callPythonChatbot(message, sessionId);
    res.json({ message: chatbotResponse });
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal server error');
  }
});

app.use((err: Error, req: Request, res: Response, next: Function) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});