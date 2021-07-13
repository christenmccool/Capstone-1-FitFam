if ($("[type='radio'][name='account_type']:checked").val() === 'ind') {
  console.log('ind')
  $("#individual-info").removeClass("d-none");
  $("#family-info").addClass("d-none");
}
if ($("[type='radio'][name='account_type']:checked").val()  === 'fam') {
  console.log('fam')
  $("#family-info").removeClass("d-none");
  $("#individual-info").addClass("d-none");
}

if ($("[type='radio'][name='family_account_type']:checked").val() === 'existing') {
  console.log('ind')
  $("#existing-family-info").removeClass("d-none");
  $("#new-family-info").addClass("d-none");
}
if ($("[type='radio'][name='family_account_type']:checked").val()  === 'new') {
  console.log('fam')
  $("#new-family-info").removeClass("d-none");
  $("#existing-family-info").addClass("d-none");
}


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
  console.log(html)
  $("#searchModal .modal-body").append(html)
});

$("#log-result-btn").click(function() {
  $("#log-result-div").removeClass("d-none");
})

$("#results-div").click(async function() {
  if (event.target.id.includes('res-comment-btn')) {
    const targetId = event.target.id
    const id = targetId.slice(-1)
    $(`#res-comment-list-${id}`).toggleClass("d-none");
  }
  if (event.target.id.includes('res-comment-save-btn')) {
    const targetId = event.target.id
    const id = targetId.slice(-1)
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
                  </li>`
    $(`#res-comment-list-${id} input`).before(html)
    $(`#res-comment-field-${id}`).val("")
  }
})


















const calendarEl = document.getElementById('calendar');
const calendar = new FullCalendar.Calendar(calendarEl, {
  headerToolbar: {
    left: 'prev,next',
    center: 'title',
    right: 'today'
  },
  dayMaxEvents: true,
  initialView: 'dayGridMonth',
  displayEventTime: false

});
calendar.render();

calendar.on('dateClick', function(info) {
  alert('clicked on ' + info.dateStr);
});
  



