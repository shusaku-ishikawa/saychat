
    var active_room_id;
    var message_offset = 0;

    var COOKIE_LAST_ROOM_ID = 'last_visited_room_id';

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
    var $loader_area = $('.loader-layer');
    var $my_modal = $('#msg_modal');
    var $my_modal_title = $('#modal_title');
    var $my_modal_body = $('#modal_body');
    var $open_btn = $('.openbtn');


 
    const MSG_COUNT_PER_READ = 10;

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

    function get_message_caption(message) {
        var char_num = 10;
        if (message.length < 10) {
            return message;
        } else {
            return message.slice(0, char_num) + '....';
        }
        
    }
    var entityMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
      };
      
    function escapeHtml (string) {
        return String(string).replace(/[&<>"'`=\/]/g, function (s) {
            return entityMap[s];
        });
    }
    function timestamp_to_readable(unixtime, as_jst) {
        Date.prototype.addHours= function(h){
            this.setHours(this.getHours()+h);
            return this;
        }

        if (as_jst) {
            var date = new Date(unixtime * 1000).addHours(9);
        } else {
            var date = new Date(unixtime * 1000);
        }
       
        var month = date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1):date.getMonth() + 1 ;
        var day = date.getDate() < 10 ? '0' + date.getDate():date.getDate();
        var hours = date.getHours() < 10 ? '0' + date.getHours():date.getHours();
        var minutes = date.getMinutes() < 10 ? '0' + date.getMinutes():date.getMinutes();
        var seconds = date.getSeconds() < 10 ? '0' + date.getSeconds():date.getSeconds();

        return(month + "/" + day + " " + hours + ":" + minutes);
    }

    function create_outgoing_message_dom(sent_by, thumbnail_url, sent_at, message, attachments, is_read) {
        console.log(sent_at)
        var $outer = $('<div>', { class: 'row outgoing_msg' });
        var $inner = $('<div>', { class: 'col-md-10 col-10 offset-md-1 sent_msg' }).appendTo($outer);
        $('<span>', { text: sent_by, class: 'sent_msg_speaker_name' }).appendTo($inner);
        $p = $('<p>', { html: escapeHtml(message).replace(/\r?\n/g, '<br />'), class:'text-wrap' });
        $p.appendTo($inner);
        $p.linkify();

        
   
        var $attchment_area = $('<div>', { class: "row" }).appendTo($inner);

        attachments.forEach(function(elem, i) {
            if (!/\.(jpe?g|png|gif|bmp)$/i.test(elem.file_name)) {
                var src = file_prev_file;
            } else {
                var src = elem.file_url;
            }
            $('<div>', { class: 'col-md-3 col-6' })
            .append($('<a>', { 
                href: elem.file_url,
                text: elem.file_name,
                download: elem.file_name,
                class: 'attachment_file '
            }))
            .append($('<img>', {
                src: src,
                class: 'img-thumbnail attachment-preview'
            }))
            .appendTo($attchment_area).append($('<br>'));
        });
        $('<span>', { class : 'outgoing_time_date', text: timestamp_to_readable(sent_at, false) }).appendTo($inner);
        if (is_read) {
            $('<div>', { class: 'outgoing_is_read' }).append($('<i>', { class : "fas fa-check" })).append($('<span>', { text: '開封済' })).appendTo($inner);
            //$('<span>', { class : 'outgoing_is_read', text: '開封済み' }).appendTo($inner);
        } else {
            $('<span>', { class : 'outgoing_is_read', text: '未読' }).appendTo($inner);
        }
        
        $('<div>', { class: 'col-md-1 col-2 outgoing_msg_img' }).append($('<img>', { src: thumbnail_url, class:'rounded-circle' })).appendTo($outer);
        return $outer
    }
    
    function create_incomming_message_dom(sent_by, thumbnail_url, sent_at, message, attachments, is_read) {
        var $outer = $('<div>', { class: 'row incoming_msg' });
        var $img_wrapper = $('<div>', { class: 'col-md-1 col-2 incoming_msg_img' }).appendTo($outer);
        

        $('<img>', { src: thumbnail_url, class: 'rounded-circle' }).appendTo($img_wrapper);
        
        var $msg_outer = $('<div>', { class: 'col-md-10 col-10 received_msg' }).appendTo($outer);
        $('<span>', { text: sent_by, class: 'incomming_msg_speaker_name' }).appendTo($msg_outer);
        var $msg_inner = $('<div>', { class: 'received_withd_msg' }).appendTo($msg_outer);
        $p = $('<p>', { html:  escapeHtml(message).replace(/\r?\n/g, '<br />'),class:'text-wrap' });
        $p.appendTo($msg_inner);
        $p.linkify();

     


        var $attachment_area = $('<div>', { class: "row" }).appendTo($msg_inner);
        attachments.forEach(function(elem, i) {
            if (!/\.(jpe?g|png|gif|bmp)$/i.test(elem.file_name)) {
                var src = file_prev_file;
            } else {
                var src = elem.file_url;
            }
            $('<div>', { class: 'col-md-3 col-6' })
            .append($('<a>', { 
                href: elem.file_url,
                text: elem.file_name,
                download: elem.file_name,
                class: 'attachment_file '
            }))
            .append($('<img>', {
                src: src,
                class: 'img-thumbnail attachment-preview'
            }))
            .appendTo($attachment_area).append($('<br>'));
        });
        var $sent_at = $('<span>', { class : 'time_date', text: timestamp_to_readable(sent_at, false) }).appendTo($msg_inner);
        
        return $outer;
    }

    function openNav() {
        $('.openbtn').hide();
        $('#mySidebar').width("375px");
        $('#main').css('marginLeft', "375px");
       
    }
  
      /* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
    function closeNav() {
        $('.openbtn').show();
        $('#mySidebar').width("0");
        $('#main').css('marginLeft', "0");
    }
      
   
    //先頭ゼロ付加
    function padZero(num) {
        var result;
        if (num < 10) {
            result = "0" + num;
        } else {
            result = "" + num;
        }
        return result;
    }
    var load_messages_call_back = function (is_initial, opponent_is_reading, opponent_last_logout) {
        var current_top_element = $div_history.children().first();
       
        return function (data) {
            data.forEach(function(obj, i) {
                message_offset = message_offset + 1;
                var is_read = false;
                if (opponent_is_reading == 'True') {
                    is_read = true;
                } else {
                    console.log(obj.sent_at + ' ' + opponent_last_logout );
                    if (obj.sent_at < opponent_last_logout) {
                        
                        is_read = true;
                    }
                }
                if (user_id == obj.speaker.pk) {
                    var $msg = create_outgoing_message_dom(obj.speaker.name, obj.speaker.thumbnail_url,  obj.sent_at, obj.message, obj.attachments, is_read);
                } else {
                    var $msg = create_incomming_message_dom(obj.speaker.name, obj.speaker.thumbnail_url, obj.sent_at, obj.message, obj.attachments, is_read);
                }
                
                $div_history.prepend($msg);
            });
            if (is_initial) {
                $div_history.animate({ scrollTop: $div_history.prop("scrollHeight")}, 100);
            } else {
                if(current_top_element.offset()) {
                    $div_history.scrollTop(current_top_element.offset().top);
                }
            }
           
        }
    }

    $(function() {
        
         // Correctly decide between ws:// and wss://
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        var ws_path = ws_scheme + '://' + window.location.host + "/ws/";
        console.log("Connecting to " + ws_path);
       
        var chatSocket = new ReconnectingWebSocket(ws_path);
        
        chatSocket.onopen = function(e) {
          console.log(e);
          $room_buttons.each(function(index, btn) {
            chatSocket.send(JSON.stringify({
                  'command': 'join',
                  'room': $(btn).attr('room_id'),
            }));
          });
        }

        chatSocket.onmessage = function(e) {
            $div_history.animate({ scrollTop: $div_history.prop("scrollHeight")}, 100);
            
            if (e == undefined) {
                return;
            }
            var data = JSON.parse(e.data);
            
            
            switch (data.msg_type) {
                case MSG_TYPE_ENTER:
                    console.log('someone joined ');
                    $room_btn = $('button[room_id="' + data.room + '"]');
                    $room_btn.attr('opponent_is_online', 'True')
                    //$room_btn.attr('opponent_is_reading', 'True');
                    
           
                    break;
                case MSG_TYPE_ENTER_ROOM:
                    console.log('he starts reading ...');
                    $room_btn = $('button[room_id="' + data.room + '"]');
                    if (data.user != user_id) {
                        $room_btn.attr('opponent_is_reading', 'True')
                        if (data.room == active_room_id) {
                            var $div = $('div[room_id="' + data.room + '"]');
                            var $already_read = $('<div>', { class: 'outgoing_is_read' }).append($('<i>', { class : "fas fa-check" })).append($('<span>', { text: '開封済' }));
                            $('div.msg_history .outgoing_is_read').replaceWith($already_read);
                        }
                    }
                    
                    break;

                case MSG_TYPE_LEAVE:
                    console.log('someone leaved');
                    $room_btn = $('button[room_id="' + data.room + '"]');
                    $room_btn.attr('opponent_is_online', 'False');
                    break;

                case MSG_TYPE_EXIT_ROOM:
                    console.log('someone exit room');
                    $room_btn = $('button[room_id="' + data.room + '"]');
                    if (data.user != user_id) {
                        $room_btn.attr('opponent_is_reading', 'False');
                        $room_btn.attr('opponent_last_logout', new Date().getTime());    
                    }
                    
                    break;
                    
                case MSG_TYPE_MESSAGE:
                    
                    messageJson = JSON.parse(data.message);
                    var is_reading = $('button[room_id="' + messageJson.room.pk + '"]').attr('opponent_is_reading') == 'True';
                    
                  
                    console.log(messageJson);
                    // 開いているチャットルームの場合は画面更新
                    if (messageJson.room.pk == active_room_id) {
                        if (user_id == messageJson.speaker.pk) {
                            //alert(is_reading);
                            var $msg = create_outgoing_message_dom(messageJson.speaker.name, messageJson.speaker.thumbnail_url, messageJson.sent_at, messageJson.message, messageJson.attachments, is_reading);
                        } else {
                            var $msg = create_incomming_message_dom(messageJson.speaker.name, messageJson.speaker.thumbnail_url, messageJson.sent_at, messageJson.message, messageJson.attachments);
                        }
                    } else {
                        // ルーム一覧を更新
                        var $target_div = $('div[room_id="' + messageJson.room.pk + '"]');
                        if ($target_div.length != 0) {
                            var $obj = $($target_div[0]);
                            $obj.find('.room_latest_message').html(get_message_caption(messageJson.message));
                            $obj.find('.chat_date').html(trim_date_str(messageJson.sent_at));
                            if ($obj.find('.has_new_message').length == 0) {
                                var $title = $obj.find('.room_title');
                                $($title[0]).append($('<span>', { text: "●", class: 'has_new_message' }));
                            }
                            
                        } else {
                            // if invited to new room
                            $('<div>', {
                                class: 'chat_list active_chat',
                                room_id: messageJson.room.pk
                            }).append($('<div>', {
                                class: 'row chat_people'
                            }).append($('<div>', {
                                class: 'col-3 chat_img'
                            }).append($('<img>', {
                                class: 'rounded-circle',
                                src: messageJson.speaker.thumbnail_url
                            })).append($('<div>', {
                                class: 'col-9 chat_ib'
                            }).append($('<div>', {
                                class: 'row'
                            }).append($('<div>', {
                                class: 'col-7'
                            }).append($('<p>', {
                                text: messageJson.room.title,
                                class: 'room_title'
                            }).append($('<span>', {
                                text: '●',
                                class: 'has_new_message'
                            }))).append($('<div>', {
                                class: 'col-5',
                                style: 'text-align: right'
                            }).append($('<p>', {
                                text: trim_date_str(messageJson.sent_at)
                            })))).append($('<div>', {
                                class: 'row'
                            }).append($('<div>', {
                                class: 'col-8'
                            }).append($('<p>', {
                                class: 'room_latest_message',
                                text: get_message_caption(messageJson.message)
                            })).append($('<div>', {
                                class: 'col-4'
                            }).append($('<button>', {
                                room_id : messageJson.room.pk,
                                type: 'button',
                                class: 'btn btn-primary btn-sm btn-block',
                                name: 'room_btn'
                            })))))))));
                        }
                    }
                    
                    $div_history.append($msg);
                    break;
                default:
                    break;
            }
        };

        chatSocket.onclose = function(e) {
            console.log('socket closed');
        };

        $input_message.focus();


        $btn_message_send.on('click', function(e) {
            

            var message = $input_message.val();
            if (message == '' && attachment_pk_list.length == 0) {
                $my_modal_body.text('メッセージを入力してください');
                $my_modal.modal('show');
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
            $preview_zone.html('');
        });
        
        $div_history.scroll(function() {
            var opponent_is_reading = $('button[room_id="' + active_room_id + '"]').attr('opponent_is_reading');
            var opponent_last_logout = $('button[room_id="' + active_room_id + '"]').attr('opponent_last_logout');
            
            if ($(this).scrollTop() == 0) {
                //alert('scroll hits top');
                call_history_api(active_room_id, message_offset, MSG_COUNT_PER_READ)
                .done(load_messages_call_back(false,  opponent_is_reading, opponent_last_logout))
                .fail(function() {
                    $my_modal_body.text('過去メッセージの取得に失敗しました');
                    $my_modal.modal('show');
                });
            }
        });

        $room_buttons.on('click' , function() {
            var room_id = $(this).attr('room_id');

            $new_message_flag = $(this).parent().parent().parent().find('.has_new_message');
            if ($new_message_flag.length > 0) {
                $($new_message_flag[0]).remove();
            }

            $.cookie(COOKIE_LAST_ROOM_ID, $(this).attr('room_id'), { expires: 7 });
            closeNav();
            $main_panel.show();
            
            $('.room-title').html($(this).attr('room_title'));

            if (room_id != active_room_id) {
                chatSocket.send(JSON.stringify({
                    'command': 'enter_room',
                    'room': room_id,
                    
                }));
                if(active_room_id != null) {
                    chatSocket.send(JSON.stringify({
                        'command': 'exit_room',
                        'room': active_room_id,
                        
                    }));
                }
            
                active_room_id = room_id;
                message_offset = 0;

                var opponent_is_reading = $(this).attr('opponent_is_reading');
                var opponent_last_logout = $(this).attr('opponent_last_logout');

                $div_history.html('');
                call_history_api(active_room_id, message_offset, MSG_COUNT_PER_READ)
                .done(load_messages_call_back(true, opponent_is_reading, opponent_last_logout))
                .fail(function() {
                    $my_modal_body.text('過去メッセージの取得に失敗しました');
                    $my_modal.modal('show');
                });
            }
        });
        
        $(document).on("keydown", "#chat-message-input", function(e){   
            if(e.shiftKey) {
                if (e.keyCode === 13){
                    $btn_message_send.click();
                    e.preventDefault();
               } 
            } 
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
            add: function (e, data) {
                
                $loader_area.show();
                data.submit();
            },
            done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
                $loader_area.hide();
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
                    class: "col-md-4 col-4 prev_col",
                }).appendTo(preview_zone);

                extension = /[^.]+$/.exec(data.files[0].name);
               
                

                //alert('image');
                $wrapper = $('<div>', { class: 'img-wrapper'} );
                $('<span>', {
                    text: data.files[0].name,
                    class:"attachment_name"
                }).appendTo($wrapper);

                //alert("png" == extension)
                if (!/\.(jpe?g|png|gif|bmp)$/i.test(data.result.url)) {
                    var src = file_prev_file;
                } else {
                    var src = data.result.url;
                }
                $('<img>', {
                    src: src,
                    class: 'img-thumbnail attachment-preview'
                }).appendTo($wrapper);
               
                
                $del_btn = $('<button>', { text:'×', class:'btn del-img-btn'})
                .appendTo($wrapper)
                .on('click', function() {
                    var $this = $(this);
                    console.log('click')
                    var i = attachment_pk_list.indexOf($(this).attr('pk'));
                    attachment_pk_list.splice(i, 1);
                    call_attachment('DELETE', $(this).attr('pk'))
                    .done(function(data) {
                        if (data.error) {
                            alert(data.error);
                            return;
                        }
                        $file_uploader.val("");
                        $this.parent().parent().remove();
                    })
                    .fail(function(data, textStatus, xhr) {
                        if (data.status == 401) {
                            window.location.href = login_url;
                        }
                        alert(xhr);
                    });
                });
                console.log('before last');
                $wrapper.appendTo($prev_col);

                
            },
            fail: function (e, data) {
                $loader_area.hide();
                $my_modal_body.text('ファイルをアップロードできませんでした');
                $my_modal.modal('show');
                return;
            }
        });
        
      
        openNav();
       
    });
