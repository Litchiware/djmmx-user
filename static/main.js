$(document).ready(function(){
  $("div.js-menu-screen.menu-screen").click(function(){
    $(this).removeClass('is-visible');
    $('.dialog').removeClass('is-visible');
  });
  $(".toggle-wx-discount").click(function(){
    var wx_id = $(this).parents("tr").children("td").eq(1).text();
    $(".hidden-form input[name='wx_discount']").attr('value', 'auto');
    $(".hidden-form form").attr("action", "/update/" + wx_id).submit();
  });
  $(".update-credit").click(function() {
    $("div.js-menu-screen.menu-screen").addClass("is-visible");
    $(".dialog").addClass("is-visible");
    $(".dialog label").text($(this).text());
    $(".dialog input[type=text]").val('');
    var td$ = $(this).parent();
    var offset = td$.offset();
    offset.left = offset.left + td$.width();
    var wx_id = $(this).parents("tr").children("td").eq(1).text();
    $(".dialog").offset(offset)
      .data({'wx_id': wx_id, 'is_positive': $(this).text() == "增加"});
  });
  $(".dialog form").submit(function(e){
    $(this).attr("action", "/update/" + $(".dialog").data('wx_id'));
    $(".dialog input[name='is_positive']").attr('value', $(".dialog").data('is_positive'));
    return true;
  });
});
