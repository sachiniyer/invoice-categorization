# Invoice Categorization API

## HTTP Endpoints
For user management

### /

#### GET
Just a simple HTML front

##### Response

```html
<p>Invoice Categorization API</p>

```
### /users

#### PUT
Creates a user if it does not exist

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| password  | sha256 string | hashed password | Yes      |

##### Response

| Parameter | Type      | Description    | Required |
|-----------|-----------|----------------|----------|
| status    | bool      | result of call | Yes      |
| jwt       | jwt token | auth jwt token | No       |


#### POST
Logs user in and give jwt with successful password

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| password  | sha256 string | hashed password | Yes      |

##### Response

| Parameter | Type      | Description    | Required |
|-----------|-----------|----------------|----------|
| status    | bool      | result of call | Yes      |
| jwt       | jwt token | auth jwt token | No       |


#### PATCH
Updates Password

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| password  | sha256 string | hashed password | Yes      |
| jwt       | jwt token     | jwt token       | Yes      |

##### Response

| Parameter | Type      | Description    | Required |
|-----------|-----------|----------------|----------|
| status    | bool      | result of call | Yes      |
| jwt       | jwt token | auth jwt token | No       |


#### Delete
Deletes a user

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| jwt       | jwt token     | jwt token       | Yes      |

##### Response

| Parameter | Type | Description    | Required |
|-----------|------|----------------|----------|
| status    | bool | result of call | Yes      |


## Websocket Endpoints

### create
Creates a new file for processing

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| file      | binary object | excel file      | Yes      |
| jwt       | jwt token     | jwt token       | Yes      |

##### Response

###### 1

| Parameter | Type | Description    | Required |
|-----------|------|----------------|----------|
| status    | bool | result of call | Yes      |

###### 2

| Parameter | Type | Description    | Required |
|-----------|------|----------------|----------|
| fileid    | num  | id of file     | Yes      |
| status    | bool | result of call | Yes      |

### list
Get files with optional file name to filter files

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| filename  | string        | name of file    | No       |
| jwt       | jwt token     | jwt token       | Yes      |

##### Response

| Parameter | Type  | Description    | Required |
|-----------|-------|----------------|----------|
| fileids   | [num] | ids of files   | Yes      |
| status    | bool  | result of call | Yes      |


### get

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| fileid    | num           | id of file      | Yes      |
| jwt       | jwt token     | jwt token       | Yes      |

##### Response

| Parameter | Type          | Description    | Required |
|-----------|---------------|----------------|----------|
| file      | binary object | file data      | No       |
| status    | bool          | result of call | Yes      |

### delete

##### Request

| Parameter | Type          | Description     | Required |
|-----------|---------------|-----------------|----------|
| username  | string        | username        | Yes      |
| fileid    | num           | id of file      | Yes      |
| jwt       | jwt token     | jwt token       | Yes      |

##### Response

| Parameter | Type | Description    | Required |
|-----------|------|----------------|----------|
| status    | bool | result of call | Yes      |
