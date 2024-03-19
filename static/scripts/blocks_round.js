window.addEventListener('DOMContentLoaded', function() {
    alignTaskRows(); // Вызываем функцию при загрузке страницы
});

window.addEventListener('resize', function() {
    alignTaskRows(); // Вызываем функцию при изменении размеров окна
});

function alignTaskRows() {
    var taskContainers = document.querySelectorAll('.container-tasks');

    taskContainers.forEach(function(taskContainer) {
        var taskRows = taskContainer.querySelectorAll('.task-row');

        taskRows.forEach(function(taskRow) {
            var childrenWidth = 0;

            taskRow.querySelectorAll('.task').forEach(function(task) {
                childrenWidth += task.offsetWidth;
            });
            if (childrenWidth + 80 < taskRow.offsetWidth) {
                taskRow.classList.remove('centered');
            } else {
                taskRow.classList.add('centered');
            }
        });
    });
}
