# invoice-categorization


An application to automatically categorize invoices specific to [Treya Partners](https://www.treyapartners.com/). It uses [AWS Bedrock Batch](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-create.html) in the backend. An example application is at https://invoice.sachiniyer.com but you should run it locally to see the full example.

### env variables
cp `env.sample` to `.env` and fill out the variable (you will need to create some AWS infrastructure for the backend)

### Backend Development
```sh
cd backend
pip install requirements.txt
flask --app server run --port 8000 --debug
```

### Frontend Development
```sh
cd frontend
npm install
npm run start
```

Written while consulting for [Treya Partners](https://www.treyapartners.com/)
