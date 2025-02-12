import { Client } from 'node-appwrite';

// This is your Appwrite function
// It's executed each time we get a request
export default async (input:any) => {
  // Why not try the Appwrite SDK?
  //
  // Set project and set API key
  // const client = new Client()
  //    .setProject(process.env.APPWRITE_FUNCTION_PROJECT_ID)
  //    .setKey(req.headers['x-appwrite-key']);

  // You can log messages to the console
  input.log('Hello, Logs!');

  // If something goes wrong, log an error
  input.error('Hello, Errors!');

  // The `req` object contains the request data
  if (input.req.method === 'GET') {
    // Send a response with the res object helpers
    // `res.text()` dispatches a string back to the client
    return input.res.text('Hello, World!');
  }

  // `res.json()` is a handy helper for sending JSON
  return input.res.json({
    motto: 'Build like a team of hundreds_',
    learn: 'https://appwrite.io/docs',
    connect: 'https://appwrite.io/discord',
    getInspired: 'https://builtwith.appwrite.io',
  });
};
