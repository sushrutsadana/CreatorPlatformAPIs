# Creator Backend

A FastAPI backend for managing creators, sending emails, and scheduling calls.

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
GMAIL_USER=your_gmail_address
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

## Testing the API

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

### Available Endpoints

1. Creator Management:
   - `POST /creators/` - Create a new creator
   - `GET /creators/` - List all creators
   - `GET /creators/{creator_id}` - Get creator details
   - `PUT /creators/{creator_id}` - Update creator
   - `DELETE /creators/{creator_id}` - Delete creator

2. Activities:
   - `POST /creators/{creator_id}/activities` - Create an activity for a creator
   - `GET /creators/{creator_id}/activities` - List activities for a creator

3. Email:
   - `POST /creators/{creator_id}/email` - Send an email to a creator

4. Calls:
   - `POST /creators/{creator_id}/call` - Schedule a call with a creator

### Example API Calls

1. Create a creator:
```bash
curl -X POST "http://localhost:8000/creators/" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "John Doe",
           "handle": "johndoe",
           "email": "john@example.com",
           "phone_number": "+1234567890"
         }'
```

2. Send an email:
```bash
curl -X POST "http://localhost:8000/creators/{creator_id}/email" \
     -H "Content-Type: application/json" \
     -d '{
           "subject": "Hello",
           "body": "This is a test email"
         }'
```

3. Schedule a call:
```bash
curl -X POST "http://localhost:8000/creators/{creator_id}/call" \
     -H "Content-Type: application/json" \
     -d '{
           "scheduled_time": "2024-02-20T10:00:00Z"
         }'
```

## Gmail Setup

To use the email functionality, you need to set up Gmail API credentials:

1. Go to the Google Cloud Console
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Use the OAuth 2.0 Playground to get a refresh token
6. Add the credentials to your `.env` file 