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

### /status

#### GET
Just gives status of application

##### Response

```json
{
    "result": bool
}
```


### /users

#### PUT
Creates a user if it does not exist

##### Request
```json
{
    "username": string,
    "password": sha256 string
}
```

##### Response

```json
{
    "result": bool,
    "jwt"?: jwt token
}
```


#### POST
Logs user in and give jwt with successful password

##### Request

```json
{
    "username": string,
    "password": sha256 string
}
```

##### Response

```json
{
    "result": bool,
    "jwt"?: jwt token
}
```


#### PATCH
Updates Password

##### Request

```json
{
    "username": string,
    "password": sha256 string,
    "jwt": jwt token
}

```

##### Response

```json
{
    "result": bool,
    "jwt": jwt token
}
```


#### Delete
Deletes a user

##### Request

```json
{
    "username": string,
    "jwt": jwt token
}

```

##### Response

```json
{
    "result": bool
}
```

## Websocket Endpoints

### create
Creates a new file for processing

##### Request

```json
{
    "username": string,
    "file": object,
    "jwt": jwt token
}

```

##### Response

###### 1

```json
{
    "result": bool
}
```

###### 2

```json
{
    "fileid": num,
    "result": bool
}
```

### list
Get files with optional file name to filter files

##### Request

```json
{
    "username": string,
    "filename"?: string,
    "jwt": jwt token
}

```

##### Response


```json
{
    "fileids": [num],
    "result": bool
}
```


### get

##### Request

```json
{
    "username": string,
    "fileid": num,
    "jwt": jwt token
}

```

##### Response


```json
{
    "file": object,
    "result": bool
}
```


### delete

##### Request

```json
{
    "username": string,
    "fileid": num,
    "jwt": jwt token
}

```

##### Response


```json
{
    "result": bool
}
```
