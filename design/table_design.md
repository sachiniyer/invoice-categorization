# Search TB
DynamoDB
| **Company Name** | **Search Result** |
|--------------|-----------|
| _string_ | _string_ |
| Google | Google is some... |
| Apple | Apple is some... |

# Users TB
MongoDB
| **Username** | **Password** |
|--------------|-----------|
| _string_ | _sha256 string_ |
| user1 | password1 |
| user2 | password2 |

# File TB
MongoDB
| **FileID** | **Username** | **Original File** | **Processed File** | **Filename** | **Ready** |
|--------------|-----------|-----------|-----------|-----------|-----------|
| _int_ | _string_ | _object_ | _object_ | _string_ | _bool_ |
| 1 | user1 | ... | ... | file1 | true |
| 2 | user1 | ... | ... | file2 | false |
