//Show correct fields in Signup Form when the template is rendered again with errors
if ($("[type='radio'][name='account_type']:checked").val() === 'ind') {
  $("#individual-info").removeClass("d-none");
  $("#family-info").addClass("d-none");
}
if ($("[type='radio'][name='account_type']:checked").val()  === 'fam') {
  $("#family-info").removeClass("d-none");
  $("#individual-info").addClass("d-none");
}

if ($("[type='radio'][name='family_account_type']:checked").val() === 'existing') {
  $("#existing-family-info").removeClass("d-none");
  $("#new-family-info").addClass("d-none");
}
if ($("[type='radio'][name='family_account_type']:checked").val()  === 'new') {
  $("#new-family-info").removeClass("d-none");
  $("#existing-family-info").addClass("d-none");
}

//Change display as Signup form is filled out
$("[type='radio'][name='account_type']").click(function() {
  if ($(this).val() === 'ind') {
    $("#individual-info").removeClass("d-none");
    $("#family-info").addClass("d-none");

    $("#existing_family_name").val("");
    $("#new_family_name").val("");
  }
  if ($(this).val() === 'fam') {
    $("#family-info").removeClass("d-none");
    $("#individual-info").addClass("d-none");
  }
});

$("[type='radio'][name='family_account_type']").click(function() {
  if ($(this).val() === 'existing') {
    $("#existing-family-info").removeClass("d-none");
    $("#new-family-info").addClass("d-none");

    $("#new_family_name").val("");
  }
  if ($(this).val() === 'new') {
    $("#new-family-info").removeClass("d-none");
    $("#existing-family-info").addClass("d-none");

    $("#existing_family_name").val("");
  }
});

//Update content of modal to display results of family search
$("#family-search-btn").click(async function() {
  $("#searchModal .modal-body").empty()
  const q = $("#family-search").val();
  const response = await axios.get('/families', {params: {q: q}});
  const results = response.data.results;

  let html = ""
  if (results.length === 0) {
    html += "No FitFam found containing that string"
  } else {
    html += '<ul class="list-group">'
    for (let result of results) {
      html += '<li class="list-group-item d-flex justify-content-between align-items-start">'
      html += `<div class="ms-2 me-auto">
                <div class="fw-bold">${result.name}</div>`
      if (result.info) {
        html += `${result.info}`
      }    
      html +=  `</div>
              <span class="badge bg-secondary rounded-pill">${result.count} members</span>`
      html += "</li>"
    }
    html += "</ul>"
  }
  $("#searchModal .modal-body").append(html)
});

//Shows add result form 
$("#log-result-btn").click(function() {
  $("#log-result-div").removeClass("d-none");
})

//Display comments on results and allow users to make comments on results
$("#results-div").click(async function() {
  if (event.target.id.includes('res-comment-btn')) {
    let targetId = event.target.id
    targetId = targetId.split('-')
    const id = targetId[targetId.length-1]
    $(`#res-comment-list-${id}`).toggleClass("d-none");
  }
  if (event.target.id.includes('res-comment-save-btn')) {
    let targetId = event.target.id
    targetId = targetId.split('-')
    const id = targetId[targetId.length-1]
    const response = await axios.post(`/results/${id}`, {res_comment : $(`#res-comment-field-${id}`).val()})
    const res_comment = response.data.result
    const html = `<li class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                      <div class="ms-2">
                        <a href="/users/${res_comment.user_id}">
                          <img src="${res_comment.user_image_url}" alt="user image" class="timeline-image me-2">
                        </a>
                        <a href="/users/${res_comment.user_id}">@${res_comment.username}</a>
                        <span class="text-muted small">${res_comment.date}}</span>
                      </div>
                      <div class="result-area text-end">
                        <div>${res_comment.res_comment}</div>
                      </div>
                    </div>

                    <div class="d-flex justify-content-end">
                    <form action="/comments/${res_comment.id}/edit">
                      <button type="submit" class="btn btn-sm btn-light text-secondary py-0 my-1 me-2" id="edit-res_comment-btn">Edit</button>
                    </form>
                    <form action="/comments/${res_comment.id}/delete" method="post">
                      <button type="submit" class="btn btn-sm btn-light text-secondary py-0 my-1" id="del-res_comment-btn">Delete</button>
                    </form>
                  </div>

                  </li>`
    $(`#res-comment-list-${id} input`).before(html)
    $(`#res-comment-field-${id}`).val("")
  }
})


//Add workouts
//Option 1: Add daily Slate workout
//Option 2: Add results of a search of the database
//Option 3: Create own workout
let dbWoList = []
$("#option1").on('click', async function() {
  $("#db-wo-search").addClass("d-none");
  $("#db-wo-list").removeClass("d-none");
  $("#add-custom-wo").addClass("d-none");
  $("#db-wo-radio").empty();


  if ($("#db-wo-radio").children().length == 0) {
    let date = $("#wo-date").val();

    const response = await axios.get('/workouts', {params: {date: date}});
    const results = response.data.results;
    if (results.length > 0) {
      for (workout of results) {
        dbWoList.push(workout);
        html = `<div class="container-fluid bg-light py-2 m-2 form-check">
                  <input type="radio" class="form-check-input mx-1 my-2" name="db-wo-list" id="wo-${workout.id}" value="${workout.id}">
                  <label class="form-check-label display-6 fw-bold" for="wo-${workout.id}">${workout.title}</label>
                  <p class="lh-sm" style="white-space:pre-wrap;">${workout.description}</p>  
                </div>`
          $("#db-wo-radio").prepend(html)  
      }
      $("#db-wo-radio").find('.form-check-input').first().attr('checked', true);
      $("#db-wo-add-btn").removeClass('d-none')
    } else {
      html = `<div class="container-fluid bg-light py-2 m-2 form-check">
                  <p class="lh-sm" style="white-space:pre-wrap;">No Slate workout posted for this day yet.</p>  
              </div>`
          $("#db-wo-radio").prepend(html)  
    }
  }
})

$("#option2").on('click', async function() {
  $("#db-wo-search").removeClass("d-none");
  $("#db-wo-list").removeClass("d-none");
  $("#add-custom-wo").addClass("d-none");
  $("#db-wo-radio").empty();
  $("#db-wo-search-field").val("")
})


$("#db-wo-search-btn").on('click', async function() {
  $("#db-wo-radio").empty();
  const date = $("#wo-date").val();

  const response = await axios.get('/workouts', {params: {q: $("#db-wo-search-field").val()}});
  const results = response.data.results;

  for (workout of results) {
    dbWoList.push(workout);
    html = `<div class="container-fluid bg-light py-2 m-2 form-check">
              <input type="radio" class="form-check-input mx-1 my-2" name="db-wo-list" id="wo-${workout.id}" value="${workout.id}">
              <label class="form-check-label display-6 fw-bold" for="wo-${workout.id}">${workout.title}</label>
              <p class="lh-sm" style="white-space:pre-wrap;">${workout.description}</p>  
            </div>`
    $("#db-wo-radio").prepend(html)  
    $("#db-wo-radio").find('.form-check-input').first().attr('checked', true);
  }
})


$("#db-wo-add-btn").on('click', async function(event) {
  const selected_wo_id = $('input[name="db-wo-list"]:checked').val();

  let title = "";
  let description = "";
  let source = "";
  let score_type = "";
  let id = "";

  for (workout of dbWoList) {
    if (workout.id == selected_wo_id) {
      title = workout.title;
      description = workout.description;
      source = workout.source;
      score_type = workout.score_type;
      id = workout.id;
    }
  }
  const date = $('#wo-date').val();


  const response = await axios.post('/workouts/add_from_db', {title:title, description:description, source:source, score_type:score_type, id:id, date:date})
  if (response.status == 200) {
    window.location.href = `/families/${response.data.results.family_id}/admin`
  }
})


$("#option3").on('click', async function() {
  $("#db-wo-search").addClass("d-none");
  $("#db-wo-list").addClass("d-none");
  $("#add-custom-wo").removeClass("d-none")

  const date = $("#wo-date").val();
  const response = await axios.post('/workouts/add', {title:$("#title").val(), description:$("#description").val(), source:"self", score_type:$("#score_type").val(), date:date})
})

