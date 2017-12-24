console.log("dvjbvjkbvjkdvjkd")
$(function(){
    	$('#signup_password, #confirm_password').change(function () {
    		if($('#signup_password').val() && $('#confirm_password').val()){
	    		console.log("both val")
                if ($('#signup_password').val() == $('#confirm_password').val()) {
	    			$('#rePassword-matching-message').html('Matching').css('color', 'green');
	    		} else{
	    			$('#signup_password-matching-message').html('');
	    			$('#rePassword-matching-message').html('Not Matching').css('color', 'red');
	    		}
    		} else {
                console.log("not")
    			if ($('#signup_password').val()==""){
		    		$('#signup_password-matching-message').html('Required Field').css('color', 'red');
		    	} else {
		    		$('#signup_password-matching-message').html("");
		    	}

		    	if ($('#confirm_password').val()==""){
		    		$('#rePassword-matching-message').html('Required Field').css('color', 'red');
		    	} else {
		    		$('#rePassword-matching-message').html("");
		    	}
    		}
    	});

    	$('#email').on("change",function () {
    		if($('#email').val()){
	    		if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($('#email').val()))
	    		{
	    			$('#email-matching-message').html('Valid').css('color', 'green');
	    		} else{
		    		$('#email-matching-message').html('Invalid email').css('color', 'red');
	    		}
    		} else {
    			$('#email-matching-message').html('Required Field').css('color', 'red');

    		}
    	});

    	$('#name').on("change",function () {
    		if($('#name').val()){
	    		if (/^[a-zA-Z0-9]+$/.test($('#name').val()))
	    		{
	    			$('#name-matching-message').html('Valid').css('color', 'green');
	    		} else {
	    			$('#name-matching-message').html('Invalid name.use only character and digits only').css('color', 'red');
	    		}
    		} else {
    			$('#name-matching-message').html('Required Field').css('color', 'red');
    		}
    	});

        $('#mobile').on("change",function () {
            if($('#mobile').val()){
                if (/^[0]?[789]\d{9}$/.test($('#mobile').val()))
                {
                    $('#mobile-matching-message').html('Valid').css('color', 'green');
                } else {
                    $('#mobile-matching-message').html('Invalid mobile.use only character and digits only').css('color', 'red');
                }
            } else {
                $('#mobile-matching-message').html('Required Field').css('color', 'red');
            }
        });

    var passwordValidation = function(){
    		if($('#signup_password').val() && $('#confirm_password').val()){
	    		if ($('#signup_password').val() == $('#confirm_password').val()) {
	    			$('#rePassword-matching-message').html('Matching').css('color', 'green');
	    			return true;
	    		} else{
	    			$('#signup_password-matching-message').html('');
	    			$('#rePassword-matching-message').html('Not Matching').css('color', 'red');
	    			return false;
	    		}
    		} else {
    			var result = false
    			if ($('#signup_password').val()==""){
		    		$('#signup_password-matching-message').html('Required Field').css('color', 'red');
		    		result = false;
		    	} else if ($('#confirm_password').val()==""){
		    		$('#rePassword-matching-message').html('Required Field').css('color', 'red');
		    		result = false;
		    	} else {
		    		$('#rePassword-matching-message').html("");
		    		$('#signup_password-matching-message').html("");
		    		result = true;
		    	}
		    	return result;
    		}
    }

    var emailValidation = function(){
    		if($('#email').val()){
	    		if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($('#email').val()))
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

    var nameValidation = function(){
    		console.log("callllll")
    		if($('#name').val()){
	    		if (/^[a-zA-Z0-9]+$/.test($('#name').val()))
	    		{
	    			$('#name-matching-message').html('Valid').css('color', 'green');
	    			return true
	    		} else {

		    		$('#name-matching-message').html('Invalid name.use only character and digits only').css('color', 'red');
		    		return false
	    		}
    		} else {
    			$('#name-matching-message').html('Required Field').css('color', 'red');
    			return false
    		}
    }

    var mobileValidation = function(){
            console.log("callllll")
            if($('#mobile').val()){
                if (/^[0]?[789]\d{9}$/.test($('#mobile').val()))
                {
                    $('#mobile-matching-message').html('Valid').css('color', 'green');
                    return true
                } else {

                    $('#mobile-matching-message').html('Invalid mobile.use only character and digits only').css('color', 'red');
                    return false
                }
            } else {
                $('#mobile-matching-message').html('Required Field').css('color', 'red');
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

    $("#submit_mover").click(function(evt){
       console.log("reg click")
       var emailResult =emailValidation();
       var nameResult=nameValidation();
       var mobileResult=mobileValidation();
       var passwordResult=passwordValidation();
       console.log(emailResult,nameResult,passwordResult,mobileResult)
       var form = $("#ragistrationFormMover");
	   var data = getFormData(form);
	   console.log("registration data === ", data)
       if(emailResult && nameResult && passwordResult && mobileResult){
       	$.ajax({
            type: "POST",
            url: "/signup/",
            data: data,
            success: function(prod_detail) {
                var data = prod_detail//JSON.parse(prod_detail)
                alert(data);
                $("#ragistrationFormMover").reset()

            }
        });
       } else {
       	console.log("validation failed")
       }
    })
})