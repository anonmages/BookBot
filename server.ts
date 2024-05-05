import express from 'express';
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
      reject('Error in Python script processing');
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.log(`Python script exited with code ${code}`);
        reject('Python script exited with an error');
      }
    });
  });
};

app.post('/message', async (req, res) => {
  const { message } = req.body;
  const sessionId = req.sessionID;

  try {
    const chatbotResponse = await callPythonChatbot(message, sessionId);
    res.json({ message: chatbotResponse });
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal server error');
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});