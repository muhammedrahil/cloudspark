#### How to Use in Javascript

### Upload File to S3 Bucket

## HTML Example

Here is an example of an HTML form that includes file upload functionality with Bootstrap styling:

```html
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <title>Hello, world!</title>
    <style>
        body{
            height: 400px;
        }
    </style>
  </head>
  <body class="d-flex justify-content-center align-items-center">
    <form action="" method="post" enctype="multipart/form-data">
        <div class="row mb-4">
           
            <input type="file" name="import_file" accept="video/*,.mkv" id="import_file" >
        </div>
        <div class="col-md-12 wrapper" id="progress-section">
            <div class="progress-bar" >
                <span class="progress-bar-fill" id="progress-bar-fill"></span>  
            </div>
            <p class="progress-text fw-bold text-center" id="progress-text">Uploaded starting...</p>
            <p class="fw-bold text-center">do not close or refresh the upload screen</p>
    
            <div class="spinner-border" id="last-progress-spinner" style="width: 3rem; height: 3rem; display: none;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
        <button type="button" class="btn btn-primary"  onclick="Uploading('import_file')" ><span>Upload</span></button>
        <button class="btn btn-danger" id="cancel-upload-button" onclick="cancelUpload()">Cancel Upload</button>
    </form>
  </body>
</html>
```

## upload file to s3 javascript Example


```javascript

async function getPresignedUrl(params) {
    try {
        params = new URLSearchParams(params)
        let url = `${BACKEND_API}${params.toString()}`
        const response = await axios.post(url);
        const data = response.data
        return [response.status , data.url, data.fields, null];
    } catch (error) {
        return [400 , null, null, error]
    }
}
```

```javascript

let cancelTokenSource;

  async function Upload_file_to_s3(file_id) {
    params = { file_name: "file_name" };
    let [status, presignedUrl, upload_fields, msg] = await getPresignedUrl(
      params
    );

    let import_file = document.getElementById(import_file_id);
    let file = import_file.files[0];

    const formData = new FormData();
    Object.keys(upload_fields).forEach((key) =>
      formData.append(key, upload_fields[key])
    );
    formData.append("file", file);

    const progress_fill = document.getElementById("progress-bar-fill");
    const progress_text = document.getElementById("progress-text");

    cancelTokenSource = axios.CancelToken.source();
    try {
      const response = await axios.post(presignedUrl, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: function (progressEvent) {
          const percentComplete = Math.floor(
            (progressEvent.loaded / progressEvent.total) * 100
          );
          progress_fill.style.width = percentComplete + "%";
          progress_text.textContent = percentComplete + "%";
        },
        cancelToken: cancelTokenSource.token,
      });
      if (response.status === 204) {
        console.log("File uploaded is completed please wait few seconds..!");

        await responce_callback_to_save_file(); // Call to your backend
      } else {
        toastr.error("File upload failed.");
      }
    } catch (error) {
      console.log(error);
    }
  }

  function cancelUpload() {
    if (cancelTokenSource) {
      cancelTokenSource.cancel("Upload canceled");
    }
  }

```

### delete file from s3 javascript Example

```javascript

async function getPresignedDeleteUrl(params) {
    try {
        params = new URLSearchParams(params)
        let url = `${BACKENDAPI}?${params.toString()}`
        const response = await axios.post(url);
        return [response.status , response.data];
    } catch (error) {
        console.log(error);
        return [400 ,null]
    }
}
```

```javascript

async function delete_file_from_s3(file_name){
    params = {
        "file_name": file_name,
    }
    let [status, url] = await getPresignedDeleteUrl(params)
    if (status == 200){
        try {
            let res =  await axios.delete(url);
            if (res.status == 204) {
                console.log("File successfully deleted from s3")
                return 
            }else {
                console.log(res);
            }
        } catch (error) {
            console.log(error);
            return 
        }
    }else {
        toastr.error(msg)
        return 
    }
}

```