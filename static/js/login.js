console.log("dvjbvjkbvjkdvjkd")
$(function(){
    	$('#signup-password, #signup-rePassword').change(function () {
    		if($('#signup-password').val() && $('#signup-rePassword').val()){
	    		if ($('#signup-password').val() == $('#signup-rePassword').val()) {
	    			$('#rePassword-matching-message').html('Matching').css('color', 'green');
	    		} else{
	    			$('#password-matching-message').html('');
	    			$('#rePassword-matching-message').html('Not Matching').css('color', 'red');
	    		}
    		} else {
    			if ($('#signup-password').val()==""){
		    		$('#password-matching-message').html('Required Field').css('color', 'red');
		    	} else {
		    		$('#password-matching-message').html("");
		    	}

		    	if ($('#signup-rePassword').val()==""){
		    		$('#rePassword-matching-message').html('Required Field').css('color', 'red');
		    	} else {
		    		$('#rePassword-matching-message').html("");
		    	}
    		}
    	});

    	$('#signup-email').on("keyup",function () {
    		if($('#signup-email').val()){
	    		if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($('#signup-email').val()))
	    		{
	    			$('#email-matching-message').html('Valid').css('color', 'green');
	    		} else{
		    		$('#email-matching-message').html('Invalid email').css('color', 'red');
	    		}
    		} else {
    			$('#email-matching-message').html('Required Field').css('color', 'red');

    		}
    	});

    	$('#signup-username').on("keyup",function () {
    		if($('#signup-username').val()){
	    		if (/^[a-zA-Z0-9]+$/.test($('#signup-username').val()))
	    		{
	    			$('#username-matching-message').html('Valid').css('color', 'green');
	    		} else {
	    			$('#username-matching-message').html('Invalid Userrname.use only character and digits only').css('color', 'red');
	    		}
    		} else {
    			$('#username-matching-message').html('Required Field').css('color', 'red');
    		}
    	});

    var passwordValidation = function(){
    		if($('#signup-password').val() && $('#signup-rePassword').val()){
	    		if ($('#signup-password').val() == $('#signup-rePassword').val()) {
	    			$('#rePassword-matching-message').html('Matching').css('color', 'green');
	    			return true;
	    		} else{
	    			$('#password-matching-message').html('');
	    			$('#rePassword-matching-message').html('Not Matching').css('color', 'red');
	    			return false;
	    		}
    		} else {
    			var result = false
    			if ($('#signup-password').val()==""){
		    		$('#password-matching-message').html('Required Field').css('color', 'red');
		    		result = false;
		    	} else if ($('#signup-rePassword').val()==""){
		    		$('#rePassword-matching-message').html('Required Field').css('color', 'red');
		    		result = false;
		    	} else {
		    		$('#rePassword-matching-message').html("");
		    		$('#password-matching-message').html("");
		    		result = true;
		    	}
		    	return result;
    		}
    }

    var emailValidation = function(){
    		if($('#signup-email').val()){
	    		if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($('#signup-email').val()))
	    		{
	    			$('#email-matching-message').html('Valid').css('color', 'green');
	    			return true
	    		} else {
		    		$('#email-matching-message').html('Invalid email').css('color', 'red');
		    		return false
	    		}
    		} else {
    			$('#email-matching-message').html('Required Field').css('color', 'red');
    			return false
    		}
    }

    var usernameValidation = function(){
    		console.log("callllll")
    		if($('#signup-username').val()){
	    		if (/^[a-zA-Z0-9]+$/.test($('#signup-username').val()))
	    		{
	    			$('#username-matching-message').html('Valid').css('color', 'green');
	    			return true
	    		} else {

		    		$('#username-matching-message').html('Invalid Userrname.use only character and digits only').css('color', 'red');
		    		return false
	    		}
    		} else {
    			$('#username-matching-message').html('Required Field').css('color', 'red');
    			return false
    		}
    }
    function getFormData($form){
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function(n, i){
            indexed_array[n['name']] = n['value'];
        });

        return indexed_array;
    }
    $("#register-btn").click(function(evt){
       console.log("reg click")
       var emailResult =emailValidation();
       var usernameResult=usernameValidation();
       var passwordResult=passwordValidation();
       console.log(emailResult,usernameResult,passwordResult)
       var form = $("#sigup-form");
	   var data = getFormData(form);
	   console.log("registration data === ", data)
       if(emailResult && usernameResult && passwordResult){
       	$.ajax({
            type: "POST",
            url: "/signup",
            data: data,
            success: function(prod_detail) {
                var data = JSON.parse(prod_detail)
                console.log(data)
            }
        });
       } else {
       	console.log("validation failed")
       }
    })
})