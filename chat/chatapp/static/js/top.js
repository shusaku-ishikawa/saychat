
    var active_room_id;


    var $input_message = $('#chat-message-input');
    var $btn_message_send = $('#send_msg_button');
    var $div_history = $('.msg_history');

    var $room_buttons = $('button[name="room_btn"]');
    var $invite_buttons = $('button[name="invite_btn"]');
    var $main_panel = $('.inbox_msg');

    var $file_uploader = $('#fileupload');
    var $preview_zone = $('#preview_zone');
    var attachment_pk_list = [];
    var $file_select_btn = $('button[name="fileupload"]');


    const MSG_TYPE_MESSAGE = 0  // For standard messages
    const MSG_TYPE_WARNING = 1  // For yellow messages
    const MSG_TYPE_ALERT = 2  // For red & dangerous alerts
    const MSG_TYPE_MUTED = 3  // For just OK information that doesn't bother users
    const MSG_TYPE_ENTER = 4  // For just OK information that doesn't bother users
    const MSG_TYPE_LEAVE = 5  // For just OK information that doesn't bother users


    function call_attachment(method, pk) {
        return $.ajax({
            url: attachment_url,
            type: 'POST',
            dataType: 'json',
            data : {
                method: method,
                pk: pk
            },
        });
    }

    function call_history_api(room_pk, offset, limit) {
        return $.ajax({
            url: history_url,
            type: 'GET',
            dataType: 'json',
            data : {
              'room_pk': room_pk,
              'offset': offset,
              'limit': limit
            }
        });
    }
    function call_invite_api(user_id) {
        return $.ajax({
            url: invite_url,
            type: 'POST',
            dataType: 'json',
            data: {
                user_id: user_id
            }
        })
    }
    function create_outgoing_message_dom(sent_at, message, attachments) {

        var $outer = $('<div>', { class: 'outgoing_msg' });
        var $inner = $('<div>', { class: 'sent_msg' }).appendTo($outer);
        $('<p>', { text: message }).appendTo($inner);
        attachments.forEach(elem => {
          $('<a>', { 
            href: elem.file_url,
            text: elem.file_name,
            download: elem.file_name,
            class: 'attachment_file '
          }).appendTo($inner).append($('<br>'));
        });
        var $sent_at = $('<span>', { class : 'time_date', text: sent_at }).appendTo($inner);
        return $outer
    }
    
    function create_incomming_message_dom(thumbnail_url, sent_at, message, attachments) {
        var $outer = $('<div>', { class: 'incoming_msg' });
        var $img_wrapper = $('<div>', { class: 'incoming_msg_img' }).appendTo($outer);
        $('<img>', { src: thumbnail_url, alt: '' }).appendTo($img_wrapper);
        
        var $msg_outer = $('<div>', { class: 'received_msg' }).appendTo($outer);
        var $msg_inner = $('<div>', { class: 'received_withd_msg' }).appendTo($msg_outer);
        $('<p>', { text: message }).appendTo($msg_inner);
        attachments.forEach(elem => {
          $('<a>', { 
            href: elem.file_url,
            text: elem.file_name,
            class: 'attachment_file',
            download: elem.file_name
          }).appendTo($msg_inner).append($('<br>'));
        });
        var $sent_at = $('<span>', { class : 'time_date', text: sent_at }).appendTo($msg_inner);

        return $outer;
    }
  
    $(function() {

         // Correctly decide between ws:// and wss://
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        var ws_path = ws_scheme + '://' + window.location.host + "/ws/";
        console.log("Connecting to " + ws_path);
        //var chatSocket = new WebSocket(ws_path);
        var chatSocket = new ReconnectingWebSocket(ws_path);
        
        chatSocket.onopen = function(e) {
          $room_buttons.each(function(index, btn) {
            chatSocket.send(JSON.stringify({
                  'command': 'join',
                  'room': $(btn).attr('room_id'),
            }));
          });
        }

        chatSocket.onmessage = function(e) {
            $div_history.animate({ scrollTop: $div_history.prop("scrollHeight")}, 1000);
            console.log(e);
            if (e == undefined) {
                return;
            }
            var data = JSON.parse(e.data);
            
            
            switch (data.msg_type) {
                case MSG_TYPE_ENTER:
                    console.log('someone joined')
                    break;
                case MSG_TYPE_LEAVE:
                    console.log('someone leaved')
                    break;
                case MSG_TYPE_MESSAGE:
                    console.log('message');
                    messageJson = JSON.parse(data.message);

                    if (user_pk == messageJson.speaker.pk) {
                        var $msg = create_outgoing_message_dom(messageJson.sent_at, messageJson.message, messageJson.attachments);
                    } else {
                        var $msg = create_incomming_message_dom(messageJson.speaker.thumbnail_url, messageJson.sent_at, messageJson.message, messageJson.attachments);
                    }
                    
                    $div_history.append($msg);
                    break;
                default:
                    break;
            }
        };

        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };

        $input_message.focus();

        $btn_message_send.on('click', function(e) {
            

            var message = $input_message.val();
            if (message == '' && attachment_pk_list.length == 0) {
                return;
            }

            chatSocket.send(JSON.stringify({
                'command': 'send',
                'room': active_room_id,
                'message': message,
                'attachment': attachment_pk_list
            }));
            $input_message.val('');
            attachment_pk_list.splice(0, attachment_pk_list.length);
        });
        
        $room_buttons.on('click' , function() {
            closeNav();
            $main_panel.show();
          
          if ($(this).attr('room_id') != active_room_id) {
            active_room_id = $(this).attr('room_id');

            $div_history.html('');
            call_history_api(active_room_id, 0, 10)
            .done(function(data) {
                //console.log(data);
                var reversed = data.reverse();
                reversed.forEach(obj => {
   
                  if (user_pk == obj.speaker.pk) {
                    var $msg = create_outgoing_message_dom(obj.sent_at, obj.message, obj.attachments);
                  } else {
                    var $msg = create_incomming_message_dom(obj.speaker.thumbnail_url, obj.sent_at, obj.message, obj.attachments);
                  }
                  
                  $div_history.append($msg);
                });
                $div_history.animate({ scrollTop: $div_history.prop("scrollHeight")}, 1000);
            })
            .fail(function() {
                alert('hello');
            });
          }
        });

        $invite_buttons.on('click', function() {
            var user_to_invite = $(this).attr('user_id');
            call_invite_api(user_to_invite)
            .done(function(data) {
                if (data.error) {
                    alert('error');
                    return;
                } else if (data.success) {
                    var room_id = data.room_id;
                    location.reload();
                }  
            })
            .fail(function(e) {
                alert('error');
            })
        });

         /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
         $file_select_btn.on('click', function() {
           $file_uploader.click();
         });

         $file_uploader.fileupload({
            dataType: 'json',
            singleFileUploads: true,
            autoUpload: true,
            replaceFileInput: false,
            done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
                if (data.result.error) {
                    alert('error');
                  
                    return;
                }
                if (attachment_pk_list.length >= 3) {
                    alert('添付ファイルは3つまでです');
                    return;
                }
                attachment_pk_list.push(data.result.pk + '');
                
                $prev_col = $('<div>', {
                    class: "col-md-2 col-4 prev_col",
                }).appendTo(preview_zone);

                extension = /[^.]+$/.exec(data.files[0].name);

                $('<span>', {
                    text: data.files[0].name,
                    class:"attachment_name"
                }).appendTo($prev_col);

                $del_span = $('<span>', {  
                }).append($('<i>', {
                  class : "fa fa-trash"
                }))
                .appendTo($prev_col)
                .on('click', function() {
                    var i = attachment_pk_list.indexOf($(this).attr('pk'));
                    attachment_pk_list.splice(i, 1);
                    call_attachment('DELETE', $(this).attr('pk'))
                    .done((data) => {
                        if (data.error) {
                            alert(data.error);
                            return;
                        }
                        $(this).parent().remove();
                    })
                    .fail(function(data, textStatus, xhr) {
                        if (data.status == 401) {
                            window.location.href = login_url;
                        }
                        alert(xhr);
                    });
                });

                
            },
            fail: function (e, data) {
                alert('失敗しました');
                return;
            }
        });
    });
