"use strict"

// Sends a new request to update the to-do list
function getPosts(page_name) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return
        updatePage(xhr)
    }
    if (page_name == "Global Stream") {
        xhr.open("GET", "/socialnetwork/get-global", true)
    } 
    else if (page_name == "Follower Stream") {
        xhr.open("GET", "/socialnetwork/get-follower", true)
    }
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status == 200) {
        let response = JSON.parse(xhr.responseText)
        updateList(response)
        return
    }

    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }


    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message) {
    let errorElement = document.getElementById("errorlist")
    errorElement.innerHTML = message
}

function updateList(data) {
    // Removes the old to-do list items
    let list = document.getElementById("my-posts-go-here")

    let items = data['posts']
    // Adds each new todo-list item to the list
    for (let i = 0; i < items.length; i++) {
        let p = items[i]

        var elementExists = document.getElementById("id_post_div_"+p.id);
        if (elementExists == null) {
            let comment_box = document.createElement("div")
            comment_box.setAttribute("class", "comment_div")
            comment_box.innerHTML = '<label> Comment: </label>' + 
                                    '<input id="id_comment_input_text_' + p.id + '" type="text">' +
                                    '<button id="id_comment_button_' + p.id +'" type="submit" onclick="addComment(' + p.id + ')">Submit</button>' +
                                    '</div>'
            list.prepend(comment_box)

            let comments = document.createElement("div")
            comments.setAttribute("id", 'my-comments-go-here-for-post-'+p.id)
            list.prepend(comments)

            let element = document.createElement("div")
            element.setAttribute("class", "post_div");
            element.setAttribute("id", "id_post_div_"+p.id);
            const time = new Date(p.creation_time)
            const creation_time = time.toLocaleDateString() + " " + time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
            element.innerHTML = '<a href=/socialnetwork/other_profile/' + p.user_id + ' class="post_profile" id="id_post_profile_' + p.id + '">' + 
                                'Post by ' + p.username + 
                                '</a>' + 
                                ' - ' + 
                                '<span class="post_text" id="id_post_text_' + p.id + '">' +
                                sanitize(p.text) + 
                                '</span>' + 
                                ' - ' + 
                                '<span class="post_date_time" id="id_post_date_time_' + p.id + '">' +
                                creation_time + 
                                '</span>' 
            // Adds the todo-list item to the HTML list
            list.prepend(element)
        }
        updateComment(data['comments'], p.id)
    }
}

function updateComment(comments, post_id) {
    let list = document.getElementById('my-comments-go-here-for-post-'+post_id)
    
    for (let i = 0; i < comments.length; i++) {
        let c = comments[i]
        if (c.post_id == post_id) {
            var elementExists = document.getElementById("id_comment_div_"+c.id);
            if (elementExists == null) {
                let element = document.createElement("div")
                element.setAttribute("class", "comment_div")
                element.setAttribute("id", "id_comment_div_"+c.id)
                const time = new Date(c.creation_time)
                const creation_time = time.toLocaleDateString() + " " + time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
                element.innerHTML = '<a href=/socialnetwork/other_profile/' + c.user_id + ' class="comment_profile" id="id_comment_profile_' + c.id + '">' + 
                                'Comment by ' + c.username + 
                                '</a>' + 
                                ' - ' + 
                                '<span class="comment_text" id="id_comment_text_' + c.id + '">' +
                                sanitize(c.text) + 
                                '</span>' + 
                                ' - ' + 
                                '<span class="comment_date_time" id="id_comment_date_time_' + c.id + '">' +
                                creation_time + 
                                '</span>' 
                list.appendChild(element)
            }
        }
    }
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addComment(post_id) {
    let itemTextElement = document.getElementById('id_comment_input_text_' + post_id)
    let itemTextValue   = itemTextElement.value

    // Clear input box and old error message (if any)
    itemTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePage(xhr)
    }

    xhr.open("POST", addItemURL, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("comment_text="+itemTextValue+"&post_id="+post_id+"&csrfmiddlewaretoken="+getCSRFToken());
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

