$(document).ready(function () {        
    // Форманы жіберуді батырма басылғанда болдырмау
    $('#setDestinationBtn, #setObstaclesBtn, #resetGameBtn, #setCharacterBtn').on('click', function (e) {
        e.preventDefault(); // Форманы жіберудің стандартты әрекетін өшіру
    });

    // Мини-ойын режимдерін қосу/өшіру
    let settingDestination = false;
    let settingObstacles = false;
    let settingCharacter = false;
    let activeMode = false; // Режим, онда тышқанды басу әрекеттері орындалмайды
    let characterX = 0;
    let characterY = 0;
    let destinationSet = false;
    let characterFixed = false;

    let selectedPath = [{ x: characterX, y: characterY }]; // Таңдалған ұяшықтардың тізбегі
    let obstacles = []; // Кедергілер тізімі
    let destination = null; // Мақсат координаттары

    // Режимдерді ауыстыру
    $('#setDestinationBtn').on('click', function () {
        settingDestination = true;
        settingObstacles = false;
        settingCharacter = false;
        activeMode = false;
        console.log('Режим: Установка цели');
    });

    $('#setObstaclesBtn').on('click', function () {
        settingDestination = false;
        settingObstacles = true;
        settingCharacter = false;
        activeMode = false;
        console.log('Режим: Установка препятствий');
    });

    $('#setCharacterBtn').on('click', function () {
        settingDestination = false;
        settingObstacles = false;
        settingCharacter = true;
        activeMode = false;
        console.log('Режим: Установка позиции персонажа');
    });

    $('#disableInteractionBtn').on('click', function () {
        settingDestination = false;
        settingObstacles = false;
        settingCharacter = false;
        activeMode = true;
        console.log('Режим: Отключение взаимодействия');
    });

    // 8x8 тор жасау
    function createGameGrid() {
        let gridContainer = $('#miniGameGrid');
        gridContainer.empty(); // Контейнердің мазмұнын тазарту

        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                let cell = $('<div></div>')
                    .addClass('grid-cell grass') // Әдепкіде шөп ұяшығы
                    .attr('data-x', i)
                    .attr('data-y', j);

                gridContainer.append(cell);
            }
        }

        console.log('Тор создан и инициализирован');
        updateDisplay(); // Мәліметтерді көрсету жаңартылды
    }

    // Торды инициализациялау
    createGameGrid();
    
    // Кейіпкер
    let character = $('<div class="character">🧍</div>');

    // Ұяшықтарға басу арқылы позицияларды өзгерту логикасы
    $('#miniGameGrid').on('click', '.grid-cell', function () {
        if (activeMode || characterFixed) {
            console.log('Нажатие отключено в текущем режиме');
            return;
        }

        let x = $(this).attr('data-x');
        let y = $(this).attr('data-y');

        // Мақсатты орнату кезінде
        if (settingDestination) {
            if (destination) {
                let previousDestinationCell = $(`.grid-cell[data-x="${destination.x}"][data-y="${destination.y}"]`);
                previousDestinationCell.removeClass('flag').addClass('grass').text('');
            }
            $(this).removeClass('grass').addClass('flag').text('🚩');
            console.log(`Цель установлена в ячейке (${x}, ${y})`);
            destination = { x: x, y: y }; // Мақсат координаттарын жаңарту
            destinationSet = true;
        } else if (settingObstacles) {
            if (!$(this).hasClass('flag') && !$(this).hasClass('character')) {
                $(this).removeClass('grass').addClass('rock').text('🪨');
                console.log(`Препятствие установлено в ячейке (${x}, ${y})`);
                obstacles.push({ x: x, y: y }); // Кедергі тізіміне қосу
            }
        } else if (settingCharacter) {
            moveCharacterTo(x, y);
            console.log(`Позиция персонажа установлена в ячейке (${x}, ${y})`);
        }

        updateDisplay(); // Мәліметтерді көрсету жаңартылды
    });

    // Кейіпкерді берілген координатқа ауыстыру
    function moveCharacterTo(x, y) {
        $('.grid-cell').removeClass('character'); // Алдыңғы позицияны тазалау
        let targetCell = $(`.grid-cell[data-x="${x}"][data-y="${y}"]`);
        targetCell.append(character);
        characterX = parseInt(x);
        characterY = parseInt(y);

        // Қозғалыс координаттарын тізбекке қосу
        selectedPath.push({ x: characterX, y: characterY });
        updateDisplay(); // Мәліметтерді көрсету жаңартылды
    }

    
    $('#moveUp').on('click', function () {
        
        let newX = characterX -1;
        let newY = characterY;
    
        // Тор шегін тексеру
        if (newX >= 0 && newX < 8 && newY >= 0 && newY < 8) {
            let targetCell = $(`.grid-cell[data-x="${newX}"][data-y="${newY}"]`);
            if (targetCell.hasClass('rock')) {
                console.log('Перемещение невозможно: препятствие');
                return;
            }

            moveCharacterTo(newX, newY);
            console.log(`Персонаж перемещен в ячейку (${newX}, ${newY})`);

            if (destinationSet && newX == destination.x && newY == destination.y) {
                console.log('Персонаж достиг цели. Дальнейшее перемещение запрещено.');
                characterFixed = true;
                $('#saveSettingsBtn').show(); // Түймені көрсету
            }
        } else {
            console.log('Перемещение невозможно: выход за пределы сетки');
        }

    });


    $('#moveDown').on('click', function () {
        
        let newX = characterX + 1;
        let newY = characterY;
    
        // Тор шегін тексеру
        if (newX >= 0 && newX < 8 && newY >= 0 && newY < 8) {
            let targetCell = $(`.grid-cell[data-x="${newX}"][data-y="${newY}"]`);
            if (targetCell.hasClass('rock')) {
                console.log('Перемещение невозможно: препятствие');
                return;
            }

            moveCharacterTo(newX, newY);
            console.log(`Персонаж перемещен в ячейку (${newX}, ${newY})`);

            if (destinationSet && newX == destination.x && newY == destination.y) {
                console.log('Персонаж достиг цели. Дальнейшее перемещение запрещено.');
                characterFixed = true;
                $('#saveSettingsBtn').show(); // Түймені көрсету
            }
        } else {
            console.log('Перемещение невозможно: выход за пределы сетки');
        }

    });


    $('#moveLeft').on('click', function () {
        
        let newX = characterX;
        let newY = characterY - 1;
    
        // Тор шегін тексеру
        if (newX >= 0 && newX < 8 && newY >= 0 && newY < 8) {
            let targetCell = $(`.grid-cell[data-x="${newX}"][data-y="${newY}"]`);
            if (targetCell.hasClass('rock')) {
                console.log('Перемещение невозможно: препятствие');
                return;
            }

            moveCharacterTo(newX, newY);
            console.log(`Персонаж перемещен в ячейку (${newX}, ${newY})`);

            if (destinationSet && newX == destination.x && newY == destination.y) {
                console.log('Персонаж достиг цели. Дальнейшее перемещение запрещено.');
                characterFixed = true;
                $('#saveSettingsBtn').show(); // Түймені көрсету
            }
        } else {
            console.log('Перемещение невозможно: выход за пределы сетки');
        }

    });


    $('#moveRight').on('click', function () {
        
        let newX = characterX;
        let newY = characterY + 1;
    
        // Тор шегін тексеру
        if (newX >= 0 && newX < 8 && newY >= 0 && newY < 8) {
            let targetCell = $(`.grid-cell[data-x="${newX}"][data-y="${newY}"]`);
            if (targetCell.hasClass('rock')) {
                console.log('Перемещение невозможно: препятствие');
                return;
            }

            moveCharacterTo(newX, newY);
            console.log(`Персонаж перемещен в ячейку (${newX}, ${newY})`);

            if (destinationSet && newX == destination.x && newY == destination.y) {
                console.log('Персонаж достиг цели. Дальнейшее перемещение запрещено.');
                characterFixed = true;
                $('#saveSettingsBtn').show(); // Түймені көрсету
            }
        } else {
            console.log('Перемещение невозможно: выход за пределы сетки');
        }

    });

    


    // Кейіпкерді пернелер арқылы жылжыту
    $(document).keydown(function (e) {
        if (activeMode || characterFixed) {
            console.log('Нажатия клавиш отключены');
            return;
        }

        let newX = characterX;
        let newY = characterY;

        switch (e.key) {
            case 'ArrowUp': newX--; break;
            case 'ArrowDown': newX++; break;
            case 'ArrowLeft': newY--; break;
            case 'ArrowRight': newY++; break;
            default: return; // Басқа пернелерді елемеу
        }

        // Тор шегін тексеру
        if (newX >= 0 && newX < 8 && newY >= 0 && newY < 8) {
            let targetCell = $(`.grid-cell[data-x="${newX}"][data-y="${newY}"]`);
            if (targetCell.hasClass('rock')) {
                console.log('Перемещение невозможно: препятствие');
                return;
            }

            moveCharacterTo(newX, newY);
            console.log(`Персонаж перемещен в ячейку (${newX}, ${newY})`);

            if (destinationSet && newX == destination.x && newY == destination.y) {
                console.log('Персонаж достиг цели. Дальнейшее перемещение запрещено.');
                characterFixed = true;
                $('#saveSettingsBtn').show(); // Түймені көрсету
            }
        } else {
            console.log('Перемещение невозможно: выход за пределы сетки');
        }
    });

    // Торды қайта орнату
    $('#resetGameBtn').on('click', function () {
        $('#saveSettingsBtn').hide(); // Сақтау түймесін жасыру
        createGameGrid(); // Торды қайта жасау
        selectedPath = []; // Тізбекті тазалау
        obstacles = []; // Кедергілерді тазалау
        destination = null; // Мақсатты тазалау
        characterX = 0; // Кейіпкер позициясын қайта орнату
        characterY = 0;
        destinationSet = false;
        characterFixed = false;
        moveCharacterTo(characterX, characterY); // Кейіпкерді бастапқы позицияға қайтару
        console.log('Сетка сброшена. Позиция персонажа возвращена к начальной.');
        updateDisplay(); // Мәліметтерді көрсету жаңартылды
    });

    // Ұяшықты әдепкі күйге қайтару
    function resetCellToDefault(cell) {
        cell.removeClass('flag rock character').addClass('grass').text('');
    }

    // Мәліметтерді көрсету және жаңарту
    function updateDisplay() {
        let pathDisplay = selectedPath.map(coord => `[${coord.x},${coord.y}]`).join(', ');
        let obstaclesDisplay = obstacles.map(coord => `[${coord.x},${coord.y}]`).join(', ');
        let destinationDisplay = destination ? `[${destination.x},${destination.y}]` : 'не установлен';
    
        $('#pathDisplay').text(`Цепочка: ${pathDisplay}`);
        $('#obstaclesDisplay').text(`Препятствия: ${obstaclesDisplay}`);
        $('#destinationDisplay').text(`Пункт назначения: ${destinationDisplay}`);
    
        // Консольде тексеру
        console.log('Цепочка:', selectedPath);
        console.log('Препятствия:', obstacles);
        console.log('Пункт назначения:', destination);
    }

    // Мәліметтерді AJAX арқылы жіберу
    function submitTestSettings() {
        let settingsData = {
            test_type: $('#test_type').val(), // Ағымдағы режим
            value_chain: selectedPath, // Жол тізбегі
            obstaclesList: obstacles, // Кедергілер тізімі
        };

        let settingsJson = JSON.stringify(settingsData);

        refreshCSRFToken();
        let new_csrf_token = getCookie('csrftoken');
        $.ajax({
            url: $('#testForm').attr('action'), // URL форманың action атрибутынан алынады
            type: 'POST',
            data: {
                purpose: 'second_factor',
                settings_data: settingsJson,
                second_factor_method: 'Test',
                csrfmiddlewaretoken: new_csrf_token,
            },
            success: function(response) {
                if (response.status === 'success') {
                    alert('Настройки успешно сохранены!');
                    console.log(response.message);
                    form.find('.error-message').hide();
                    form.find('.success-message').text(response.message).show();
                    setTimeout(() => {
                        window.location.reload(); // Сақталғаннан кейін бетті қайта жүктеу
                    }, 1000);
                }
            },
            error: function(xhr) {
                const errorResponse = JSON.parse(xhr.responseText);
                form.find('.success-message').hide();
                form.find('.error-message').text(errorResponse.message).show();
                console.log(errorResponse.message);
            }
        });
    }

    // Сақтау түймесі үшін өңдеуіш
    $('#saveSettingsBtn').on('click', function () {
        submitTestSettings();
    });
});
