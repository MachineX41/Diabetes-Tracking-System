/*
const { spawn } = require('child_process');

// Formu ve butonu seç
const form = document.getElementById('loginForm');

form.addEventListener('submit', (event) => {
  event.preventDefault();

  // Kullanıcı verilerini al
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const role = document.getElementById('role').value;

  // JSON verisini oluştur
  const jsonData = JSON.stringify({ username, password, role });

  // Python betiğini başlat
  const py = spawn('python', ['path_to_your_python_script.py']);

  // Veriyi Python'a gönder
  py.stdin.write(jsonData + "\n");  // \n ekle ki Python satırı tam alsın
  py.stdin.end();

  // Python'dan gelen yanıtı al ve kullan
  py.stdout.on('data', (data) => {
    console.log(`Python cevabı: ${data.toString()}`);
  });
});*/