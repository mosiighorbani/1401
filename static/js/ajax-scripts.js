// ajax like post
$(function(){
    $('#ajaxbtn').click(function(){
        console.log('ajax button is clicked !!')
        $.ajax({
            url : '/blog/ajax-post',
            // data : $('form').serialize(),
            data : '',
            type : 'GET',
            success : function(response) {console.log(response);},
            error : function(response) {console.log(response);},

        });
    });
});
// end of ajax like post

