
$(document).ready(function(){
  console.log('fask app is running ..')
  $('.reply-link').click(function(){
    $(this).next('form').toggle()
  })
});