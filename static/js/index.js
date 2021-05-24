// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};
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
        author: "",
        rows: [],
        thumbs: [],
        users: [],
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
                author: d_var,
                
            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                comment: app.vue.add_comment,
                title: app.vue.add_title,
                author: d_var,
                status: 0,
    
            });
            
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
            app.init();
        });
    };

    app.reset_form = function () {
        app.vue.add_comment = "";
        app.vue.author = "";
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


   

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_contact: app.add_contact,
        set_add_status: app.set_add_status,
        set_like_status: app.set_like_status,
        get_like_status: app.get_like_status,
        delete_contact: app.delete_contact,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    // Generally, this will be a network call to the server to
    // load the data.
    // For the moment, we 'load' the data from a string.
    app.init = () => {
        axios.get(load_contacts_url).then(function (response) {
            app.vue.rows = app.enumerate(response.data.rows);
            app.vue.users = app.enumerate(response.data.users);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
