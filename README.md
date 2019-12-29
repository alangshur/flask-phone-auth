# roam-backend

## Setting Up Environment

First, install all python dependencies. This setup is written for `pip3` version 19.3.1 and `python3` version 3.7.4. Additionally, it is recommended to setup a virtual environment using `virtualenv` version 16.7.5.

`$ pip3 install -r requirements.txt`

To setup and enter the virtual environment, use the following command.

`$ virtualenv venv ; source venv/bin/activate`

Once in the virtual environment, you will be prompted with a notice from `autoenv` (if not, back out of the project directory and reenter). Once responding `yes` on this prompt, the appropriate environment variables will be loaded.

## Running the Flask App

With the project and environment set up, simply run the following command to launch the app. The environment simulated will default to development, although this can be modified in the `.env` file or by re-exporting the `FLASK_ENV` environment variable.

`$ flask run`

## Database Schema

### `pot_users` Collection

`db.pot_users` is a collection for managing pending users that are undergoing phone authentication. It uses a TTL index that automatically cleans documents after five minutes.

```javascript
{
    'phone_number': '[PHONE_NUMBER]',
    'validation_code': '[VALIDATION_CODE]'
}
```

## `users` Collection

`db.users` is a collection for managing validated users.

```javascript
{
    'user_id': '[USER_ID]',
    'account_amount': '[ACCOUNT_AMOUNT]',
    'access_token': '[ACCESS_TOKEN]',
    'last_game_id': '[LAST_GAME_ID]'
}
```

## Twilio

### Creating Messaging Service

```python
service = twilio.messaging \
    .services \
    .create(friendly_name='Roam Messaging Service')
```

### Adding Phone Numbers

```python
phone_number = twilio.messaging \
    .services('[SERVICE_SID]') \
    .phone_numbers \
    .create(phone_number_sid='[PHONE_NUMBER_SID]')
```

### Creating Alphanumeric Sender ID

```python
alpha_sender = twilio.messaging \
    .services('[SERVICE_SID]') \
    .alpha_senders \
    .create(alpha_sender='Roam')
```

## Security

### Frontend Security

- Encrypted access tokens and API URIs

### Backend Security

- HTTPS/SSL
- Access token verification
- Speed limiting and fraudulent movement detection (in consecutive nav API requests)
- Protected location extraction (GMS/GPS in iOS)
- Rate limiting on IP and access token
- Mongo database encryption
