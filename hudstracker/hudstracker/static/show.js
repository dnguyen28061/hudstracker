// On selection of either dinner or lunch, webpage reloads to show menus
function show_menu() {
    // meal is equal to the select value of lunch or dinner 
    var e = document.getElementById('meal');
    var meal = e.options[e.selectedIndex].value;
    // if lunch, display the lunch form, if dinner then display dinner 
    if (meal == "lunch") {
        $("#lunch_form").css('display', 'block');
        $("#dinner_form").css('display', 'none');
    } else if (meal == "dinner") {
        $("#dinner_form").css('display', 'block');
        $("#lunch_form").css('display', 'none');
    }
    show_nutrition();

}

function show_nutrition() {
    // See whether the user chose lunch or dinner 
    var e = document.getElementById('meal');
    var meal = e.options[e.selectedIndex].value;
    // nutrition is the menu of items and its nutrition (passed in from flask)
    var nutrition;
    var choice;
    var counter;
    if (meal == "lunch") {
        nutrition = lunch_nutrition;
        choice = document.getElementById('lunch');
        counter = choice.options[choice.selectedIndex].value;
    } else if (meal == "dinner") {
        nutrition = dinner_nutrition;
        // get the index of the menu item selected 
        choice = document.getElementById('dinner');
        counter = choice.options[choice.selectedIndex].value;
    }
    // insert a table with nutritional info 
    var mytable = '<table class="table"><tr><th>Food</th><th>Calories</th><th>Serving Size</th><th>Carbohydrates</th><th>Fat</th><th>Protein</th></tr><tr><td>' + nutrition[counter - 1].title + '</td><td>' + nutrition[counter - 1].calories + '</td><td>' + nutrition[counter - 1].serving_size + '</td><td>' + nutrition[counter - 1].carbs + ' g</td><td>' + nutrition[counter - 1].fat + ' g</td><td>' + nutrition[counter - 1].protein + ' g</td></table>';
    document.getElementById('nutrition').innerHTML = mytable;
}
