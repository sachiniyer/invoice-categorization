# Search TB
DynamoDB

Primary Key - **Company**

| **Company Name** | **Search Result** |
|------------------|-------------------|
| _string_         | _string_          |
| Google           | Google is some... |
| Apple            | Apple is some... |

# Users TB
DynamoDB

Primary Key - **Username**

| **Username** | **Password**    |
|--------------|-----------------|
| _string_     | _sha256 string_ |
| user1        | password1       |
| user2        | password2       |

# File Object Storage 
S3

2 buckets (same structure)
1. uploaded
2. processed

| **FileID** | **File Content** |
|------------|------------------|
| _string_      | _object_         |
| 1          | file1            |
| 2          | file1            |

# File TB
DynamoDB

Primary Key - **FileID**
Sort Key - **Username**

| **FileID** | **Username** | **Filename** | **Processed** |
|------------|--------------|--------------|---------------|
| _string_   | _string_     | _string_     | _bool_        |
| 1          | user1        | file1        | false         |
| 2          | user2        | file2        | true          |

