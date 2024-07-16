function updateCartUI(data, itemId) {
    console.log("Updating UI with data:", data);

    if (data.hasOwnProperty('removed') && data.removed) {
        // If the item was removed, delete it from the UI
        $(`#cart-item-${itemId}`).remove();
    } else if (itemId && data.hasOwnProperty('quantity')) {
        // Update quantity if it's provided
        $(`#quantity-${itemId}`).text(data.quantity);
        
        // If quantity is 0, remove the item from the cart UI
        if (data.quantity === 0) {
            $(`#cart-item-${itemId}`).remove();
        }
    }
    
    if (data.hasOwnProperty('amount')) {
        $('#amount').text(parseFloat(data.amount).toFixed(2));
    }
    
    if (data.hasOwnProperty('totalamount')) {
        $('#totalamount').text(parseFloat(data.totalamount).toFixed(2));
    }

    // Update shipping charge visibility based on totalamount
    if (data.totalamount === 0) {
        $('#shipping-charge').hide();
    } else {
        $('#shipping-charge').show();
    }

    // If the cart is empty, show empty cart message
    if ($('.cart-item').length === 0) {
        $('#cart-container').html("<h1 class='text-center'>Cart is Empty</h1>");
    }
}

function updateCart(url, id) {
    $.ajax({
        type: "GET",
        url: url,
        data: {
            prod_id: id
        },
        success: function(data) {
            console.log("Received data:", data);
            if (url.includes('removecart')) {
                // If this was a remove action, force removal from UI
                $(`#cart-item-${id}`).remove();
            }
            updateCartUI(data, id);
        },
        error: function(xhr, status, error) {
            console.error("Error updating cart:", error);
            alert("An error occurred while updating the cart. Please try again.");
        }
    });
}

$('.plus-cart').click(function() {
    if ($(this).prop('disabled')) return;
    var id = $(this).attr("pid").toString();
    console.log("plus pid=", id);
    updateCart("/pluscart", id);
});

$('.minus-cart').click(function() {
    if ($(this).prop('disabled')) return;
    var id = $(this).attr("pid").toString();
    console.log("minus pid=", id);
    updateCart("/minuscart", id);
});

$('.remove-cart').click(function() {
    if ($(this).prop('disabled')) return;
    var id = $(this).attr("pid").toString();
    console.log("remove pid=", id);
    updateCart("/removecart", id);
});
