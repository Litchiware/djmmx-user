$(document).ready(function(){
  $(".find-users button").click(function(){
    var target_name = $(this).next().val();
    var trs$ = $(".rwd-table tbody tr");
    trs$.css("display", "table-row");
    trs$.each(function(){
      var username = $(this).children(":first").text();
      if (username.indexOf(target_name) == -1){
        $(this).css("display", "none");
      }
    });
  });
  $("div.js-menu-screen.menu-screen").click(function(){
    $(this).removeClass('is-visible');
    $('.dialog').removeClass('is-visible');
  });
  $(".toggle-wx-discount").click(function(){
    var phone_number = $(this).parents("tr").children("td").eq(1).text().substring(0, 11);
    $(".hidden-form input[name='wx_discount']").attr('value', 'auto');
    $(".hidden-form form").attr("action", "/update/" + phone_number).submit();
  });
  $("a[class^='update-']").click(function() {
    form_div$ = $("#" + $(this).attr('class')+'-form')
    $("div.js-menu-screen.menu-screen").addClass("is-visible");
    form_div$.addClass("is-visible");
    if (form_div$.attr('id') == 'update-credit-form'){
      form_div$.children("input[type=submit]").val($(this).text());
      form_div$.data({'is_positive': $(this).text() == "增加"});
    }
    form_div$.children("input[type=text]").val('');
    var last_link$ = $(this).parent().children(":last");
    var offset = last_link$.offset();
    offset.left = offset.left + $(this).width();
    form_div$.offset(offset)
    var phone_number = $(this).parents("tr").children("td").eq(1).text().substring(0, 11);
    form_div$.data({'phone_number': phone_number});
  });
  $(".dialog form").submit(function(e){
    phone_number = $(this).parent().data('phone_number')
    $(this).attr("action", "/update/" + phone_number);
    if ($(this).parent().attr('id') == 'update-credit-form'){
      $(this).children("input[name='is_positive']").attr('value', $(this).parent().data('is_positive'));
    }
    return true;
  });
});
