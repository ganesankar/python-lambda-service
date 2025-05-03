# AWS Lambda Serverless Project

## Setup

1. Install Node.js and npm
2. Install Serverless Framework globally:
   ```
   npm install -g serverless
   ```

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Local Development

Run locally with Serverless Offline:
```
serverless offline
```

## Deployment

Deploy to AWS:
```
serverless deploy
```

## Project Structure
- `src/`: Lambda function source code
- `serverless.yml`: Serverless configuration
- `requirements.txt`: Python dependencies
