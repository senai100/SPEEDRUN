# Arquivo combinado (app_combined.py)

from flask import Flask, render_template, request, jsonify
from datetime import datetime
from flask_cors import CORS
import speedtest

app = Flask(__name__)
CORS(app)

historico = []

# Conteúdo HTML
html_content = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speed Test</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }

        .container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }

        h1 {
            color: #007bff;
            text-align: center;
        }

        button.btn-primary {
            background-color: #007bff;
            border: none;
            width: 100%;
        }

        .loader {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #3498db;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: none;
            margin: 20px auto;
        }

        p#resultado {
            margin-top: 20px;
            text-align: center;
        }

        h3 {
            margin-top: 30px;
            color: #007bff;
            text-align: center;
        }

        #historicoIcone {
            cursor: pointer;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>Speed Test</h1>

        <button class="btn btn-primary" onclick="testarVelocidade()" id="btnTestarVelocidade">Testar Velocidade</button>

        <div class="loader" id="loader"></div>

        <p id="resultado"></p>

        <h3>Histórico <span id="historicoIcone" onclick="toggleHistorico()">&#x1F550;</span></h3>
        <ul id="historico">
            <!-- O histórico será preenchido dinamicamente com JavaScript -->
        </ul>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    <script>
        $(document).ready(function () {
            carregarHistorico();
        });

        function testarVelocidade() {
            if ($('#btnTestarVelocidade').prop('disabled')) {
                alert('Aguarde, a conexão está sendo testada.');
                return;
            }

            $('#btnTestarVelocidade').prop('disabled', true);
            $('#loader').show();

            // Fazer a solicitação para a rota do servidor Flask que testa a velocidade
            $.ajax({
                url: 'http://localhost:5000/speedtest',  // Atualize para o seu endereço e porta do servidor Flask
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    $('#loader').hide();
                    var resultado = `Velocidade de Download: ${formatarBytes(data.velocidade_download)}ps<br>`;
                    resultado += `Velocidade de Upload: ${formatarBytes(data.velocidade_upload)}ps`;
                    $('#resultado').html(resultado);

                    $('#btnTestarVelocidade').prop('disabled', false);

                    adicionarAoHistorico(data.velocidade_download, data.velocidade_upload);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $('#loader').hide();
                    console.error('Erro ao testar a velocidade:', textStatus, errorThrown);
                    $('#resultado').text('Erro ao testar a velocidade.');

                    $('#btnTestarVelocidade').prop('disabled', false);
                }
            });
        }

        function carregarHistorico() {
            $.ajax({
                url: 'http://localhost:5000/historico',  // Atualize para o seu endereço e porta do servidor Flask
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    preencherHistorico(data);
                },
                error: function () {
                    console.error('Erro ao carregar o histórico.');
                }
            });
        }

        function preencherHistorico(historico) {
            var listaHistorico = $('#historico');
            listaHistorico.empty();

            if (historico.length > 0) {
                for (var i = 0; i < historico.length; i++) {
                    var teste = historico[i];
                    var itemHistorico = `<li>${teste.data_hora} - Download: ${formatarBytes(teste.velocidade_download)}ps, Upload: ${formatarBytes(teste.velocidade_upload)}ps</li>`;
                    listaHistorico.append(itemHistorico);
                }
            } else {
                listaHistorico.append('<li>Nenhum teste no histórico.</li>');
            }
        }

        function toggleHistorico() {
            $('#historico').slideToggle();
        }

        function formatarBytes(bytes) {
            var sizes = ['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps'];
            if (bytes == 0) return '0 bps';
            var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1000)));
            return Math.round(bytes / Math.pow(1000, i), 2) + ' ' + sizes[i];
        }

        function adicionarAoHistorico(velocidadeDownload, velocidadeUpload) {
            $.ajax({
                url: 'http://localhost:5000/adicionar-ao-historico',  // Atualize para o seu endereço e porta do servidor Flask
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ velocidade_download: velocidadeDownload, velocidade_upload: velocidadeUpload }),
                success: function (data) {
                    console.log('Teste adicionado ao histórico.');
                },
                error: function () {
                    console.error('Erro ao adicionar teste ao histórico.');
                }
            });
        }
    </script>
</body>

</html>
"""

@app.route('/')
def index():
    return html_content

@app.route('/historico')
def obter_historico():
    return jsonify(historico)

@app.route('/adicionar-ao-historico', methods=['POST'])
def adicionar_ao_historico():
    dados = request.get_json()
    velocidade_download = dados['velocidade_download']
    velocidade_upload = dados['velocidade_upload']
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    teste = {'data_hora': data_hora, 'velocidade_download': velocidade_download, 'velocidade_upload': velocidade_upload}
    historico.append(teste)
    return jsonify({'status': 'ok'})

@app.route('/speedtest')
def testar_velocidade():
    st = speedtest.Speedtest()
    velocidade_download = st.download()
    velocidade_upload = st.upload()
    return jsonify({'velocidade_download': velocidade_download, 'velocidade_upload': velocidade_upload})

if __name__ == '__main__':
    app.run(debug=True)