// This will be the object that will contain the Vue attributes
// and be used to initialize it.

let app = {};

// Thanks to https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string
/**
 * Format bytes as human-readable text.
 *
 * @param bytes Number of bytes.
 * @param si True to use metric (SI) units, aka powers of 1000. False to use
 *           binary (IEC), aka powers of 1024.
 * @param dp Number of decimal places to display.
 *
 * @return Formatted string.
 */
function humanFileSize(bytes, si=false, dp=1) {
    const thresh = si ? 1000 : 1024;
  
    if (Math.abs(bytes) < thresh) {
      return bytes + ' B';
    }
  
    const units = si
      ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
      : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
    let u = -1;
    const r = 10**dp;
  
    do {
      bytes /= thresh;
      ++u;
    } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1);
  
  
    return bytes.toFixed(dp) + ' ' + units[u];
  }

Vue.filter('reverse', function(value) {
    // slice to make a copy of array, then reverse the copy
    return value.slice().reverse();
  });

function change()
{
    this.style.height = "64px";
}

let a = 'unliked';
var d_var =  document.getElementById("d_elem").value;
// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        add_mode: false,
        add_comment: "",
        add_title: "",
        add_link: "",
        author: "",
        rows: [],
        class_rows: [],
        thumbs: [],
        users: [],
        file_name: null, // File name
        file_type: null, // File type
        file_date: null, // Date when file uploaded
        file_path: null, // Path of file in GCS
        file_size: null, // Size of uploaded file
        download_url: null, // URL to download a file
        uploading: false, // upload in progress
        image_bool: false, // set to true if an image is uploaded
        deleting: false, // delete in progress
        delete_confirmation: false, // Show the delete confirmation thing.
        msg: "test",
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.complete = (rows) => {
        // Initializes useful fields of images.
        rows.map((thumb) => {
            thumb.status = 0;

        })
    };

 
    app.add_contact = function () {
        axios.post(add_contact_url,
            {
                
                comment: app.vue.add_comment,
                title: app.vue.add_title,
                link: app.vue.add_link, 
                author: d_var,
                image_bool: app.vue.image_bool
                
            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                comment: app.vue.add_comment,
                title: app.vue.add_title,
                link: app.vue.add_link, 
                author: d_var,
                status: 0,
    
            });
            app.vue.image_bool = false;
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
            app.init();
        });
    };

    app.reset_form = function () {
        app.vue.add_comment = "";
        app.vue.author = "";
        app.vue.add_title = "";
        app.vue.add_link = "";
    };

    app.delete_contact = function(row_idx) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_contact_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
            for (let i = 0; i < app.vue.users.length; i++) {
                if (app.vue.users[i].item_id === id) {
                    app.vue.users.splice(i, 1);
                    app.enumerate(app.vue.users);
                }
            }
            });
    };

  

    app.set_add_status = function (new_status) {
        
        app.vue.add_mode = new_status;
    };


    app.set_like_status = function (row_idx, status, prevStatus) {
        app.vue.rows[row_idx].status = status;
        axios.post(like_url,
                {
                    id: app.vue.rows[row_idx].id,
                    field: 'likes',
                    value: status,
                    prev: prevStatus


                });

        app.init()
    };

    app.get_like_status = function (row_idx) {
        let x = app.vue.rows[row_idx];
        console.log(x.status); 
    };


    app.set_star_status = function (row_idx, status, prevStatus) {
        axios.post(star_url,
                {
                    id: app.vue.class_rows[row_idx].id,
                    field: 'star',
                    value: status,
                    prev: prevStatus


                });

        app.init()
    };

    app.get_star_status = function (row_idx) {
        let x = app.vue.class_rows[row_idx];
        console.log(x.status);
    };

   
    app.file_info = function () {
        if (app.vue.file_path) {
            let info = "";
            if (app.vue.file_size) {
                info = humanFileSize(app.vue.file_size.toString(), si=true);
            }
            if (app.vue.file_type) {
                if (info) {
                    info += " " + app.vue.file_type;
                } else {
                    info = app.vue.file_type;
                }
            }
            if (info) {
                info = " (" + info + ")";
            }
            if (app.vue.file_date) {
                let d = new Sugar.Date(app.vue.file_date + "+00:00");
                info += ", uploaded " + d.relative();
            }
            return app.vue.file_name + info;
        } else {
            return "";
        }
    }


    app.set_result = function (r) {
        // Sets the results after a server call.
        app.vue.file_name = r.data.file_name;
        app.vue.file_type = r.data.file_type;
        app.vue.file_date = r.data.file_date;
        app.vue.file_path = r.data.file_path;
        app.vue.file_size = r.data.file_size;
        app.vue.download_url = r.data.download_url;
    }

    app.upload_file = function (event) {
        let input = event.target;
        let file = input.files[0];
        if (file) {
            app.vue.uploading = true;
            app.vue.image_bool = true;
            let file_type = file.type;
            let file_name = file.name;
            let file_size = file.size;
            // Requests the upload URL.
            axios.post(obtain_gcs_url, {
                action: "PUT",
                mimetype: file_type,
                file_name: file_name
            }).then ((r) => {
                let upload_url = r.data.signed_url;
                let file_path = r.data.file_path;
                // Uploads the file, using the low-level interface.
                let req = new XMLHttpRequest();
                // We listen to the load event = the file is uploaded, and we call upload_complete.
                // That function will notify the server `of the location of the image.
                req.addEventListener("load", function () {
                    app.upload_complete(file_name, file_type, file_size, file_path);
                });
                // TODO: if you like, add a listener for "error" to detect failure.
                req.open("PUT", upload_url, true);
                req.send(file);
            });
        }
    }

    app.upload_complete = function (file_name, file_type, file_size, file_path) {
        // We need to let the server know that the upload was complete;
        axios.post(notify_url, {
            file_name: file_name,
            file_type: file_type,
            file_path: file_path,
            file_size: file_size,
        }).then( function (r) {
            app.vue.uploading = false;
            app.vue.file_name = file_name;
            app.vue.file_type = file_type;
            app.vue.file_path = file_path;
            app.vue.file_size = file_size;
            app.vue.file_date = r.data.file_date;
            app.vue.download_url = r.data.download_url;
            console.log(app.vue.download_url);
        });
    }

    app.delete_file = function () {
        if (!app.vue.delete_confirmation) {
            // Ask for confirmation before deleting it.
            app.vue.delete_confirmation = true;
        } else {
            // It's confirmed.
            app.vue.delete_confirmation = false;
            app.vue.deleting = true;
            // Obtains the delete URL.
            let file_path = app.vue.file_path;
            axios.post(obtain_gcs_url, {
                action: "DELETE",
                file_path: file_path,
            }).then(function (r) {
                let delete_url = r.data.signed_url;
                if (delete_url) {
                    // Performs the deletion request.
                    let req = new XMLHttpRequest();
                    req.addEventListener("load", function () {
                        app.deletion_complete(file_path);
                    });
                    // TODO: if you like, add a listener for "error" to detect failure.
                    req.open("DELETE", delete_url);
                    req.send();

                }
            });
        }
    };

    app.deletion_complete = function (file_path) {
        // We need to notify the server that the file has been deleted on GCS.
        axios.post(delete_url, {
            file_path: file_path,
        }).then (function (r) {
            // Poof, no more file.
            app.vue.deleting =  false;
            app.vue.file_name = null;
            app.vue.file_type = null;
            app.vue.file_date = null;
            app.vue.file_path = null;
            app.vue.download_url = null;
        })
    }

    app.download_file = function () {
        if (app.vue.download_url) {
            let req = new XMLHttpRequest();
            req.addEventListener("load", function () {
                app.do_download(req);
            });
            req.responseType = 'blob';
            req.open("GET", app.vue.download_url, true);
            req.send();
        }
    };

    app.do_download = function (req) {
        // This Machiavellic implementation is thanks to Massimo DiPierro.
        // This creates a data URL out of the file we downloaded.
        let data_url = URL.createObjectURL(req.response);
        // Let us now build an a tag, not attached to anything,
        // that looks like this:
        // <a href="my data url" download="myfile.jpg"></a>
        let a = document.createElement('a');
        a.href = data_url;
        a.download = app.vue.file_name;
        // and let's click on it, to do the download!
        a.click();
        // we clean up our act.
        a.remove();
        URL.revokeObjectURL(data_url);
    };

    app.computed = {
        file_info: app.file_info,
    };


    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_contact: app.add_contact,
        set_add_status: app.set_add_status,
        set_like_status: app.set_like_status,
        get_like_status: app.get_like_status,
        set_star_status: app.set_star_status,
        get_star_status: app.get_star_status,
        delete_contact: app.delete_contact,
        upload_file: app.upload_file, // Uploads a selected file
        delete_file: app.delete_file, // Delete the file.
        download_file: app.download_file, // Downloads it.
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        computed: app.computed,
        methods: app.methods
    });

    // And this initializes it.
    // Generally, this will be a network call to the server to
    // load the data.
    // For the moment, we 'load' the data from a string.
    app.init = () => {
        axios.get(file_info_url)
            .then(function (r) {
                app.set_result(r);
            });
        axios.get(load_contacts_url).then(function (response) {
            app.vue.rows = app.enumerate(response.data.rows);
            app.vue.users = app.enumerate(response.data.users);
        });
        axios.get(load_classes_url).then(function (response) {
            app.vue.class_rows = app.enumerate(response.data.class_rows);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
