import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import random
import time
import json
import re
from supabase import create_client, Client

# Configuração da página
st.set_page_config(
    page_title="StudyFlow Pro - Vença a Procrastinação",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("""
    🚨 **CONFIGURAÇÃO NECESSÁRIA**
    
    Para funcionar, você precisa configurar as credenciais do Supabase:
    
    **No Streamlit Community Cloud:**
    1. Vá em Settings → Secrets
    2. Adicione:
    ```
    [secrets]
    SUPABASE_URL = "sua_url_aqui"
    SUPABASE_KEY = "sua_chave_aqui"
    ```
    
    **Para testar localmente:**
    1. Crie arquivo `.streamlit/secrets.toml` 
    2. Adicione o mesmo conteúdo acima
    3. Adicione `.streamlit/` no .gitignore
    """)
    st.stop()

# Inicializar cliente Supabase
@st.cache_resource
def init_supabase():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"❌ Erro ao conectar com Supabase: {str(e)}")
        st.error("👆 Verifique suas credenciais!")
        return None

supabase = init_supabase()

# CSS personalizado para visual reconfortante e funcional
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #E3F2FD 0%, #F8FBFF 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #E3F2FD 0%, #F8FBFF 100%);
    }
    
    .study-card {
        background: rgba(187, 222, 251, 0.3);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #81C784;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .technique-card {
        background: rgba(255, 193, 7, 0.1);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #FFC107;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0,0,0,0.1);
    }
    
    .pomodoro-timer {
        background: linear-gradient(45deg, #FF5722, #FF8A65);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .habit-card {
        background: rgba(179, 229, 252, 0.4);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #64B5F6;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0,0,0,0.1);
    }
    
    .motivational-quote {
        background: linear-gradient(90deg, #BBDEFB, #E1F5FE);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-style: italic;
        border: 2px solid #90CAF9;
        margin: 1rem 0;
    }
    
    .procrastination-killer {
        background: linear-gradient(45deg, #E8F5E8, #C8E6C9);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .memory-technique {
        background: linear-gradient(45deg, #F3E5F5, #E1BEE7);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #9C27B0;
        margin: 0.5rem 0;
    }
    
    .login-card {
        background: linear-gradient(45deg, #E3F2FD, #F8FBFF);
        padding: 2rem;
        border-radius: 20px;
        border: 3px solid #42A5F5;
        margin: 2rem 0;
        text-align: center;
    }
    
    .calendar-day {
        padding: 0.5rem;
        margin: 0.2rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    
    .study-day {
        background-color: #81C784;
        color: white;
    }
    
    .today {
        background-color: #FFB74D;
        color: white;
    }
    
    .normal-day {
        background-color: #F5F5F5;
    }
    
    h1, h2, h3 {
        color: #1565C0;
    }
    
    .success-message {
        background: linear-gradient(90deg, #C8E6C9, #A5D6A7);
        padding: 1rem;
        border-radius: 8px;
        color: #2E7D32;
        font-weight: bold;
    }
    
    .challenge-badge {
        background: linear-gradient(45deg, #FFD54F, #FFECB3);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: #F57F17;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .streak-counter {
        background: linear-gradient(45deg, #FF6B6B, #FFE66D);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .connection-status {
        background: linear-gradient(45deg, #4CAF50, #8BC34A);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .error-status {
        background: linear-gradient(45deg, #FF5722, #FF8A65);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Dados das técnicas
MOTIVATIONAL_QUOTES = [
    "💫 Cada pequeno passo te leva mais perto dos seus sonhos!",
    "🌟 O conhecimento é o único investimento que sempre dá lucro!",
    "🚀 Você está construindo seu futuro, uma lição por vez!",
    "🌱 O crescimento acontece fora da zona de conforto!",
    "💪 Persistência é a chave para transformar sonhos em realidade!",
    "🎯 Foco no processo, não apenas no resultado!",
    "✨ Cada dia de estudo é um dia mais próximo da sua meta!",
    "🏆 Você é mais forte do que imagina e mais capaz do que acredita!",
    "🌸 Paciência e consistência florescem em grandes conquistas!",
    "💎 Você está lapidando a joia mais preciosa: sua mente!",
    "🔥 A disciplina é escolher entre o que você quer agora e o que você mais quer!",
    "⭐ Pequenos progressos diários levam a grandes resultados!",
    "🌈 Depois da tempestade, sempre vem o arco-íris do sucesso!",
    "🎪 Transforme seu estudo numa aventura emocionante!",
    "💝 Cada erro é um presente que te ensina algo novo!"
]

ANTI_PROCRASTINATION_TIPS = [
    {
        "title": "🍅 Técnica Pomodoro",
        "description": "25 min de foco + 5 min de pausa. Depois de 4 ciclos, pausa de 30 min.",
        "action": "Comece AGORA com apenas 1 pomodoro!"
    },
    {
        "title": "🐸 Eat the Frog",
        "description": "Faça a tarefa mais difícil PRIMEIRO, quando sua energia está no máximo.",
        "action": "Qual é seu 'sapo' de hoje?"
    },
    {
        "title": "⚡ Regra dos 2 Minutos",
        "description": "Se algo leva menos de 2 minutos, faça IMEDIATAMENTE.",
        "action": "Liste 3 tarefas de 2 minutos e faça agora!"
    },
    {
        "title": "🧱 Chunking",
        "description": "Divida grandes tarefas em pedaços menores e conquiste um por vez.",
        "action": "Divida sua próxima tarefa em 3 partes!"
    },
    {
        "title": "🎯 Implementação de Intenções",
        "description": "'Quando X acontecer, eu farei Y'. Ex: 'Quando sentar na mesa, abro o livro'.",
        "action": "Crie sua frase 'Se-Então' agora!"
    },
    {
        "title": "🔄 Habit Stacking",
        "description": "Conecte um novo hábito a um já existente. 'Depois de X, farei Y'.",
        "action": "Que hábito você pode empilhar no estudo?"
    }
]

MEMORY_TECHNIQUES = [
    {
        "name": "🏰 Palácio da Memória",
        "description": "Associe informações a lugares familiares. Caminhe mentalmente e 'coloque' conhecimento em cada cômodo.",
        "example": "Para lembrar a lista de compras, coloque cada item em um cômodo da sua casa."
    },
    {
        "name": "🔗 Associação",
        "description": "Conecte informações novas a conhecimentos que já possui.",
        "example": "Para lembrar que Mitocôndria gera energia, pense: 'Mito(lenda) + Côndria(energia) = Lenda da Energia'."
    },
    {
        "name": "📖 Storytelling",
        "description": "Transforme informações em uma história interessante e memorável.",
        "example": "Para decorar fórmulas, crie uma história onde cada elemento é um personagem."
    },
    {
        "name": "🎵 Ritmo e Rima",
        "description": "Crie músicas, rimas ou ritmos para memorizar sequências.",
        "example": "Para lembrar π (3,14159...), crie uma música com os números."
    },
    {
        "name": "🖼️ Visualização",
        "description": "Crie imagens mentais vívidas e exageradas para lembrar conceitos.",
        "example": "Para lembrar que H2O é água, imagine 2 patos (H) nadando em um lago (O)."
    },
    {
        "name": "🔤 Acrônimos",
        "description": "Use as primeiras letras para criar palavras ou frases memoráveis.",
        "example": "LARANJA para lembrar: Ler, Anotar, Resumir, Associar, Narrar, Julgar, Aplicar."
    }
]

STUDY_TECHNIQUES = [
    {
        "name": "📚 Revisão Ativa",
        "description": "Não apenas releia - questione, resuma, explique em voz alta.",
        "tip": "Ensine o conteúdo para um amigo imaginário!"
    },
    {
        "name": "🔄 Repetição Espaçada",
        "description": "Revise em intervalos crescentes: 1 dia, 3 dias, 1 semana, 1 mês.",
        "tip": "Use este app! Ele já faz isso automaticamente."
    },
    {
        "name": "🎯 Prática de Recuperação",
        "description": "Teste-se sem olhar as respostas. Flashcards são perfeitos!",
        "tip": "Cubra as respostas e tente lembrar ativamente."
    },
    {
        "name": "🔀 Intercalação",
        "description": "Alterne entre diferentes tipos de problemas ou matérias.",
        "tip": "Não estude apenas matemática por 3h. Alterne com outras matérias!"
    },
    {
        "name": "📝 Elaboração",
        "description": "Explique COMO e POR QUE algo funciona, não apenas o QUE é.",
        "tip": "Sempre pergunte: 'Por que isso faz sentido?'"
    }
]

# Sistema de Login com Código Pessoal
def show_login():
    """Exibe tela de login com código pessoal"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1565C0; font-size: 3rem; margin-bottom: 0.5rem;">🔐 StudyFlow Pro</h1>
        <h3 style="color: #42A5F5; font-weight: 300;">Entre com seu código pessoal</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="procrastination-killer">
        <h4>🎯 Como funciona:</h4>
        <ul>
            <li><strong>Primeira vez?</strong> Crie um código único (ex: joao2025, maria_estudos)</li>
            <li><strong>Já tem conta?</strong> Digite seu código para acessar seus dados</li>
            <li><strong>Funciona em qualquer dispositivo!</strong> Basta lembrar do código</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        access_code = st.text_input(
            "🔑 Seu Código Pessoal:",
            placeholder="Ex: joao2025, maria_estudos",
            help="Use letras, números e _ (sem espaços). Mínimo 4 caracteres.",
            max_chars=50,
            key="login_code"
        )
        
        if st.button("🚀 Entrar / Criar Conta", use_container_width=True):
            if access_code and len(access_code) >= 4:
                # Validar código (só letras, números e _)
                if re.match("^[a-zA-Z0-9_]+$", access_code):
                    st.session_state.user_id = access_code.lower()
                    st.session_state.logged_in = True
                    st.success(f"✅ Bem-vindo(a), {access_code}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Use apenas letras, números e _ (sem espaços)")
            else:
                st.error("❌ Código deve ter pelo menos 4 caracteres")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dicas de segurança
    st.markdown("""
    <div class="technique-card">
        <h4>💡 Dicas para um bom código:</h4>
        <ul>
            <li><strong>Fácil de lembrar:</strong> seu_nome2025, joao_estudos</li>
            <li><strong>Único:</strong> não use códigos óbvios como "1234"</li>
            <li><strong>Anote em local seguro:</strong> se esquecer, perde os dados!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def get_user_id():
    """Obtém ID do usuário via código pessoal"""
    return st.session_state.get('user_id', None)

# Funções do banco de dados
def load_subjects():
    """Carrega matérias do banco"""
    if not supabase:
        return []
    
    try:
        user_id = get_user_id()
        if not user_id:
            return []
            
        result = supabase.table('subjects').select("*").eq('user_id', user_id).execute()
        
        subjects = []
        for row in result.data:
            # Converter review_dates de JSONB para dict com datetime
            review_dates = {}
            for key, date_str in row['review_dates'].items():
                review_dates[key] = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            subject = {
                'id': row['id'],
                'name': row['name'],
                'notes': row['notes'],
                'study_date': datetime.strptime(row['study_date'], '%Y-%m-%d').date(),
                'difficulty': row['difficulty'],
                'confidence': row['confidence'],
                'study_method': row['study_method'],
                'review_dates': review_dates,
                'completed_reviews': row['completed_reviews'] or [],
                'reset_count': row['reset_count'] or 0
            }
            subjects.append(subject)
        
        return subjects
    except Exception as e:
        st.error(f"Erro ao carregar matérias: {str(e)}")
        return []

def save_subject(subject):
    """Salva uma matéria no banco"""
    if not supabase:
        return False
    
    try:
        user_id = get_user_id()
        if not user_id:
            return False
        
        # Converter review_dates para formato JSON
        review_dates_json = {}
        for key, date_obj in subject['review_dates'].items():
            if isinstance(date_obj, datetime):
                review_dates_json[key] = date_obj.isoformat()
            else:
                review_dates_json[key] = date_obj
        
        data = {
            'user_id': user_id,
            'name': subject['name'],
            'notes': subject['notes'],
            'study_date': subject['study_date'].isoformat(),
            'difficulty': subject['difficulty'],
            'confidence': subject['confidence'],
            'study_method': subject['study_method'],
            'review_dates': review_dates_json,
            'completed_reviews': subject['completed_reviews'],
            'reset_count': subject['reset_count']
        }
        
        if 'id' in subject:
            # Atualizar matéria existente
            result = supabase.table('subjects').update(data).eq('id', subject['id']).execute()
        else:
            # Criar nova matéria
            result = supabase.table('subjects').insert(data).execute()
            subject['id'] = result.data[0]['id']
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar matéria: {str(e)}")
        return False

def delete_subject(subject_id):
    """Deleta uma matéria do banco"""
    if not supabase:
        return False
    
    try:
        supabase.table('subjects').delete().eq('id', subject_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar matéria: {str(e)}")
        return False

def load_habits():
    """Carrega hábitos do banco"""
    if not supabase:
        return []
    
    try:
        user_id = get_user_id()
        if not user_id:
            return []
            
        result = supabase.table('habits').select("*").eq('user_id', user_id).execute()
        
        habits = []
        for row in result.data:
            # Converter completed_days de array para list de dates
            completed_days = []
            if row['completed_days']:
                for date_str in row['completed_days']:
                    completed_days.append(datetime.strptime(date_str, '%Y-%m-%d').date())
            
            habit = {
                'id': row['id'],
                'name': row['name'],
                'trigger': row['trigger_text'],
                'category': row['category'],
                'difficulty': row['difficulty'],
                'completed_days': completed_days,
                'best_streak': row['best_streak'] or 0,
                'created_date': datetime.strptime(row['created_date'], '%Y-%m-%d').date()
            }
            habits.append(habit)
        
        return habits
    except Exception as e:
        st.error(f"Erro ao carregar hábitos: {str(e)}")
        return []

def save_habit(habit):
    """Salva um hábito no banco"""
    if not supabase:
        return False
    
    try:
        user_id = get_user_id()
        if not user_id:
            return False
        
        # Converter completed_days para array de strings
        completed_days_str = [date.isoformat() for date in habit['completed_days']]
        
        data = {
            'user_id': user_id,
            'name': habit['name'],
            'trigger_text': habit.get('trigger', ''),
            'category': habit['category'],
            'difficulty': habit.get('difficulty', ''),
            'completed_days': completed_days_str,
            'best_streak': habit.get('best_streak', 0),
            'created_date': habit['created_date'].isoformat()
        }
        
        if 'id' in habit:
            # Atualizar hábito existente
            result = supabase.table('habits').update(data).eq('id', habit['id']).execute()
        else:
            # Criar novo hábito
            result = supabase.table('habits').insert(data).execute()
            habit['id'] = result.data[0]['id']
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar hábito: {str(e)}")
        return False

def delete_habit(habit_id):
    """Deleta um hábito do banco"""
    if not supabase:
        return False
    
    try:
        supabase.table('habits').delete().eq('id', habit_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar hábito: {str(e)}")
        return False

def load_user_settings():
    """Carrega configurações do usuário"""
    if not supabase:
        return {}
    
    try:
        user_id = get_user_id()
        if not user_id:
            return {}
            
        result = supabase.table('user_settings').select("*").eq('user_id', user_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            # Criar configurações padrão
            default_settings = {
                'user_id': user_id,
                'daily_quote': random.choice(MOTIVATIONAL_QUOTES),
                'study_streak': 0,
                'last_study_date': None,
                'total_study_time': 0
            }
            
            supabase.table('user_settings').insert(default_settings).execute()
            return default_settings
    except Exception as e:
        st.error(f"Erro ao carregar configurações: {str(e)}")
        return {}

def save_user_settings(settings):
    """Salva configurações do usuário"""
    if not supabase:
        return False
    
    try:
        user_id = get_user_id()
        if not user_id:
            return False
            
        result = supabase.table('user_settings').upsert(settings).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar configurações: {str(e)}")
        return False

# Inicialização do session_state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'subjects' not in st.session_state:
        st.session_state.subjects = []
    if 'habits' not in st.session_state:
        st.session_state.habits = []
    if 'user_settings' not in st.session_state:
        st.session_state.user_settings = {}
    if 'daily_quote' not in st.session_state:
        st.session_state.daily_quote = random.choice(MOTIVATIONAL_QUOTES)
    if 'pomodoro_timer' not in st.session_state:
        st.session_state.pomodoro_timer = 0
    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False

# Carregar dados do usuário logado
def load_user_data():
    if st.session_state.logged_in and get_user_id():
        st.session_state.subjects = load_subjects()
        st.session_state.habits = load_habits()
        st.session_state.user_settings = load_user_settings()
        st.session_state.daily_quote = st.session_state.user_settings.get('daily_quote', random.choice(MOTIVATIONAL_QUOTES))

# Função para calcular streak de estudos
def calculate_study_streak():
    if not st.session_state.subjects:
        return 0
    
    today = datetime.now().date()
    dates = []
    
    # Coletar todas as datas de revisão concluídas
    for subject in st.session_state.subjects:
        for phase in subject['completed_reviews']:
            review_date = subject['review_dates'][phase]
            if isinstance(review_date, datetime):
                review_date = review_date.date()
            dates.append(review_date)
    
    # Ordenar datas
    dates = sorted(set(dates), reverse=True)
    
    if not dates:
        return 0
    
    # Calcular streak consecutivo
    streak = 0
    current_date = today
    
    for date in dates:
        if date == current_date or date == current_date - timedelta(days=1):
            streak += 1
            current_date = date - timedelta(days=1)
        else:
            break
    
    return streak

# Timer Pomodoro
def pomodoro_timer():
    st.subheader("🍅 Timer Pomodoro - Vença a Procrastinação!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        timer_type = st.selectbox(
            "Escolha seu foco:",
            ["🎯 Foco (25 min)", "☕ Pausa Curta (5 min)", "🏖️ Pausa Longa (15 min)"]
        )
        
        timer_minutes = {
            "🎯 Foco (25 min)": 25,
            "☕ Pausa Curta (5 min)": 5,
            "🏖️ Pausa Longa (15 min)": 15
        }
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("▶️ Iniciar Timer", use_container_width=True):
                st.session_state.pomodoro_timer = timer_minutes[timer_type] * 60
                st.session_state.timer_active = True
        
        with col_b:
            if st.button("⏹️ Parar Timer", use_container_width=True):
                st.session_state.timer_active = False
                st.session_state.pomodoro_timer = 0
        
        # Display do timer
        if st.session_state.pomodoro_timer > 0:
            minutes = st.session_state.pomodoro_timer // 60
            seconds = st.session_state.pomodoro_timer % 60
            
            st.markdown(f"""
            <div class="pomodoro-timer">
                ⏱️ {minutes:02d}:{seconds:02d}
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.timer_active:
                time.sleep(1)
                st.session_state.pomodoro_timer -= 1
                if st.session_state.pomodoro_timer <= 0:
                    st.balloons()
                    st.success("🎉 Pomodoro concluído! Você venceu a procrastinação!")
                st.rerun()

# Função para calcular próximas datas de revisão
def calculate_review_dates(start_date):
    dates = {
        'hoje': start_date,
        '3_dias': start_date + timedelta(days=3),
        '1_semana': start_date + timedelta(days=7),
        '1_mes': start_date + timedelta(days=30)
    }
    return dates

# Função para criar mini calendário da semana
def create_weekly_calendar(subjects):
    st.subheader("📅 Calendário da Semana")
    
    today = datetime.now().date()
    start_week = today - timedelta(days=today.weekday())
    
    cols = st.columns(7)
    days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    
    study_dates = []
    for subject in subjects:
        for phase, date in subject['review_dates'].items():
            if isinstance(date, datetime):
                date = date.date()
            if start_week <= date <= start_week + timedelta(days=6):
                study_dates.append(date)
    
    for i, day in enumerate(days):
        current_date = start_week + timedelta(days=i)
        with cols[i]:
            if current_date == today:
                st.markdown(f'<div class="calendar-day today">{day}<br>{current_date.day}</div>', unsafe_allow_html=True)
            elif current_date in study_dates:
                st.markdown(f'<div class="calendar-day study-day">{day}<br>{current_date.day}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="calendar-day normal-day">{day}<br>{current_date.day}</div>', unsafe_allow_html=True)
    
    st.markdown("🟢 **Verde**: Dias de revisão | 🟠 **Laranja**: Hoje | ⚪ **Cinza**: Dias normais")

def main():
    init_session_state()
    
    # Verificar se usuário está logado
    if not st.session_state.get('logged_in', False):
        show_login()
        return
    
    # Carregar dados do usuário
    if not st.session_state.subjects and not st.session_state.habits:
        load_user_data()
    
    # Status da conexão
    if supabase:
        st.markdown("""
        <div class="connection-status">
            ✅ Conectado ao banco de dados - Seus dados estão seguros!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-status">
            ❌ Erro de conexão - Configure suas credenciais do Supabase!
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Header principal
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1565C0; font-size: 3rem; margin-bottom: 0.5rem;">🧠 StudyFlow Pro</h1>
        <h3 style="color: #42A5F5; font-weight: 300;">Vença a procrastinação e turbine sua memória!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Streak Counter
    streak = calculate_study_streak()
    st.markdown(f"""
    <div class="streak-counter">
        🔥 Sequência de Estudos: {streak} dia(s) consecutivos!
        {" 🚀 Você está pegando fogo!" if streak >= 7 else " 💪 Continue assim!" if streak >= 3 else " 🌱 Todo grande começo é assim!"}
    </div>
    """, unsafe_allow_html=True)
    
    # Frase motivacional do dia
    st.markdown(f"""
    <div class="motivational-quote">
        <h4>{st.session_state.daily_quote}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegação
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        page = st.selectbox(
            "Escolha uma seção:",
            ["🏠 Dashboard", "📖 Adicionar Matéria", "📚 Minhas Matérias", "✅ Meus Hábitos", "🧠 Técnicas de Estudo", "⚡ Anti-Procrastinação", "🍅 Timer Pomodoro"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Estatísticas")
        st.metric("Matérias Cadastradas", len(st.session_state.subjects))
        st.metric("Hábitos Ativos", len(st.session_state.habits))
        st.metric("Sequência de Estudos", f"{streak} dias")
        
        # Informações do usuário
        st.markdown("---")
        st.markdown(f"**👤 Logado como:** `{get_user_id()}`")
        st.caption("Seus dados ficam salvos com este código")
        
        if st.button("🚪 Trocar Conta"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.subjects = []
            st.session_state.habits = []
            st.rerun()
        
        # Badges de conquistas
        st.markdown("### 🏆 Conquistas")
        if streak >= 3:
            st.markdown('<div class="challenge-badge">🔥 3 Dias Seguidos!</div>', unsafe_allow_html=True)
        if streak >= 7:
            st.markdown('<div class="challenge-badge">⭐ Uma Semana!</div>', unsafe_allow_html=True)
        if streak >= 30:
            st.markdown('<div class="challenge-badge">🚀 Um Mês!</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Nova Frase Motivacional"):
            st.session_state.daily_quote = random.choice(MOTIVATIONAL_QUOTES)
            # Salvar nova frase no banco
            settings = st.session_state.user_settings.copy()
            settings['daily_quote'] = st.session_state.daily_quote
            save_user_settings(settings)
            st.rerun()
    
    # Dashboard Principal
    if page == "🏠 Dashboard":
        st.header("📊 Seu Painel de Controle")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Progresso Hoje")
            today = datetime.now().date()
            
            # Verificar matérias para revisar hoje
            due_today = []
            for subject in st.session_state.subjects:
                for phase, date in subject['review_dates'].items():
                    if isinstance(date, datetime):
                        date = date.date()
                    if date == today and phase not in subject['completed_reviews']:
                        due_today.append((subject['name'], phase))
            
            if due_today:
                st.warning(f"📚 {len(due_today)} revisões pendentes hoje!")
                for name, phase in due_today:
                    st.write(f"• {name} ({phase})")
            else:
                st.success("🎉 Todas as revisões de hoje concluídas!")
            
            # Hábitos de hoje
            habits_today = 0
            habits_done_today = 0
            for habit in st.session_state.habits:
                habits_today += 1
                if today in habit['completed_days']:
                    habits_done_today += 1
            
            if habits_today > 0:
                progress = habits_done_today / habits_today
                st.metric("Hábitos Hoje", f"{habits_done_today}/{habits_today}", f"{progress:.1%}")
            
        with col2:
            st.subheader("🎯 Dica Anti-Procrastinação do Dia")
            daily_tip = random.choice(ANTI_PROCRASTINATION_TIPS)
            st.markdown(f"""
            <div class="procrastination-killer">
                <h4>{daily_tip['title']}</h4>
                <p>{daily_tip['description']}</p>
                <strong>💡 Ação: {daily_tip['action']}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Timer Pomodoro rápido
        st.markdown("---")
        pomodoro_timer()
        
        # Calendário da semana
        if st.session_state.subjects:
            create_weekly_calendar(st.session_state.subjects)
    
    # Timer Pomodoro (página dedicada)
    elif page == "🍅 Timer Pomodoro":
        st.header("🍅 Centro de Foco - Timer Pomodoro")
        
        st.markdown("""
        <div class="procrastination-killer">
            <h3>🎯 Como usar o Pomodoro para vencer a procrastinação:</h3>
            <ol>
                <li><strong>Escolha UMA tarefa específica</strong></li>
                <li><strong>Configure o timer para 25 minutos</strong></li>
                <li><strong>Trabalhe com foco TOTAL até o alarme</strong></li>
                <li><strong>Faça uma pausa de 5 minutos</strong></li>
                <li><strong>Repita! A cada 4 pomodoros, pausa de 15 min</strong></li>
            </ol>
            <p><strong>🧠 Dica Pro:</strong> Desligue notificações, coloque o celular longe, e comunique que não quer ser interrompido!</p>
        </div>
        """, unsafe_allow_html=True)
        
        pomodoro_timer()
        
        # Estatísticas de foco
        st.subheader("📊 Suas Estatísticas de Foco")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pomodoros Hoje", "0", "Comece agora! 🚀")
        with col2:
            st.metric("Tempo Total de Foco", "0min", "Cada minuto conta! ⏰")
        with col3:
            st.metric("Maior Sequência", "0", "Construa seu recorde! 🏆")
    
    # Página: Anti-Procrastinação
    elif page == "⚡ Anti-Procrastinação":
        st.header("⚡ Arsenal Anti-Procrastinação")
        
        st.markdown("""
        <div class="procrastination-killer">
            <h3>🎯 Diagnóstico Rápido: Por que você procrastina?</h3>
            <p>Marque o que mais te identifica:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Checklist de procrastinação
        reasons = [
            "😰 A tarefa parece muito grande/complexa",
            "🎯 Não sei exatamente o que fazer",
            "😴 Estou sem energia/motivação",
            "📱 Me distraio facilmente",
            "😨 Tenho medo de falhar/errar",
            "⏰ Sempre deixo para a última hora",
            "🤔 Não vejo a importância da tarefa"
        ]
        
        selected_reasons = []
        cols = st.columns(2)
        for i, reason in enumerate(reasons):
            with cols[i % 2]:
                if st.checkbox(reason, key=f"reason_{i}"):
                    selected_reasons.append(reason)
        
        # Técnicas específicas baseadas no diagnóstico
        if selected_reasons:
            st.markdown("### 🎯 Técnicas Personalizadas Para Você:")
            
            for reason in selected_reasons:
                if "grande/complexa" in reason:
                    st.markdown("""
                    <div class="technique-card">
                        <h4>🧱 Para tarefas grandes: CHUNKING</h4>
                        <p>Divida em pedaços de 15-25 min cada. Ex: "Ler capítulo 1" vira "Ler páginas 1-5", "Fazer resumo páginas 1-5"</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if "não sei" in reason:
                    st.markdown("""
                    <div class="technique-card">
                        <h4>🗺️ Para falta de clareza: PLANEJAMENTO</h4>
                        <p>Passe 5 min escrevendo: "O que EXATAMENTE preciso fazer?" Liste cada passo pequeno.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if "energia" in reason:
                    st.markdown("""
                    <div class="technique-card">
                        <h4>⚡ Para baixa energia: EAT THE FROG</h4>
                        <p>Faça a tarefa mais difícil LOGO DEPOIS do café da manhã, quando sua energia está no pico!</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Todas as técnicas
        st.markdown("### 🛠️ Todas as Técnicas Anti-Procrastinação")
        
        for tip in ANTI_PROCRASTINATION_TIPS:
            with st.expander(f"{tip['title']} - Clique para saber mais", expanded=False):
                st.write(tip['description'])
                st.info(f"💡 **Ação prática:** {tip['action']}")
        
        # Desafio diário
        st.markdown("""
        <div class="procrastination-killer">
            <h3>🏆 Desafio Anti-Procrastinação de Hoje</h3>
            <p><strong>Escolha UMA técnica acima e use AGORA por apenas 10 minutos!</strong></p>
            <p>10 minutos é quase nada, mas pode quebrar o ciclo da procrastinação! 🚀</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Página: Técnicas de Estudo
    elif page == "🧠 Técnicas de Estudo":
        st.header("🧠 Laboratório de Técnicas de Estudo")
        
        tab1, tab2 = st.tabs(["🧠 Técnicas de Memória", "📚 Métodos de Estudo"])
        
        with tab1:
            st.subheader("🧠 Turbine Sua Memória")
            
            for technique in MEMORY_TECHNIQUES:
                with st.expander(f"{technique['name']} - Domine esta técnica!", expanded=False):
                    st.write(technique['description'])
                    st.example(f"**Exemplo prático:** {technique['example']}")
                    
                    # Mini-exercício prático
                    st.markdown("**🎯 Pratique agora:**")
                    if "Palácio" in technique['name']:
                        practice = st.text_input("Liste 5 cômodos da sua casa:", key=f"practice_{technique['name']}")
                        if practice:
                            st.success("Perfeito! Agora imagine colocando uma informação importante em cada cômodo!")
                    
                    elif "Associação" in technique['name']:
                        practice = st.text_input("Digite algo que quer memorizar:", key=f"practice_{technique['name']}")
                        if practice:
                            st.success(f"Ótimo! Agora pense: '{practice}' te lembra de quê que você já conhece?")
        
        with tab2:
            st.subheader("📚 Métodos Científicos de Estudo")
            
            for technique in STUDY_TECHNIQUES:
                st.markdown(f"""
                <div class="memory-technique">
                    <h4>{technique['name']}</h4>
                    <p>{technique['description']}</p>
                    <strong>💡 Dica: {technique['tip']}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Teste de retenção
        st.markdown("---")
        st.subheader("🧪 Teste Sua Retenção")
        
        st.markdown("""
        <div class="procrastination-killer">
            <h4>🎯 Mini-Quiz: Teste o que acabou de aprender!</h4>
            <p>Responder perguntas fortalece a memória (Prática de Recuperação!)</p>
        </div>
        """, unsafe_allow_html=True)
        
        quiz_question = st.radio(
            "Qual técnica é melhor para memorizar uma lista de compras?",
            ["📝 Apenas escrever várias vezes", "🏰 Palácio da Memória", "🎵 Fazer uma música", "Todas são igualmente eficazes"]
        )
        
        if st.button("✅ Verificar Resposta"):
            if "Palácio da Memória" in quiz_question:
                st.success("🎉 Correto! O Palácio da Memória é perfeito para listas!")
            else:
                st.info("🤔 Quase! O Palácio da Memória é especialmente eficaz para listas sequenciais!")
    
    # Página: Adicionar Matéria
    elif page == "📖 Adicionar Matéria":
        st.header("📝 Adicionar Nova Matéria")
        
        # Dica motivacional para adicionar matérias
        st.markdown("""
        <div class="procrastination-killer">
            <h4>🎯 Dica Pro: Acabou de estudar? Adicione IMEDIATAMENTE!</h4>
            <p>Não espere "organizar depois" - isso é procrastinação disfarçada! 😉</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_subject_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                subject_name = st.text_input(
                    "Nome da Matéria:",
                    placeholder="Ex: Eletrônica - Transistor BJT"
                )
                
                subject_notes = st.text_area(
                    "Resumo do que estudou (use técnicas de elaboração!):",
                    placeholder="Ex: Aprendi que transistores BJT têm 3 terminais (base, coletor, emissor). Base controla corrente entre coletor-emissor. Tipo NPN conduz quando base positiva. Pratiquei cálculo de ganho beta.",
                    height=120
                )
                
                # Técnica de estudo usada
                study_method = st.selectbox(
                    "Que técnica você usou hoje?",
                    ["📚 Leitura ativa", "🎯 Prática de problemas", "🔄 Revisão espaçada", "🧠 Resumos/mapas mentais", "👥 Ensinar alguém", "🎵 Mnemônicos", "Outra"]
                )
            
            with col2:
                study_date = st.date_input(
                    "Data do Estudo:",
                    value=datetime.now().date()
                )
                
                difficulty = st.selectbox(
                    "Como foi a dificuldade?",
                    ["😊 Fácil - dominei bem", "🤔 Médio - preciso praticar mais", "😰 Difícil - preciso revisar bastante"]
                )
                
                confidence = st.slider(
                    "Confiança (1-10):",
                    min_value=1, max_value=10, value=7,
                    help="1 = Não entendi nada, 10 = Posso ensinar alguém"
                )
            
            submitted = st.form_submit_button("➕ Adicionar Matéria", use_container_width=True)
            
            if submitted and subject_name:
                review_dates = calculate_review_dates(datetime.combine(study_date, datetime.min.time()))
                
                new_subject = {
                    'name': subject_name,
                    'notes': subject_notes,
                    'study_date': study_date,
                    'difficulty': difficulty,
                    'confidence': confidence,
                    'study_method': study_method,
                    'review_dates': review_dates,
                    'completed_reviews': [],
                    'reset_count': 0
                }
                
                # Salvar no banco
                if save_subject(new_subject):
                    st.session_state.subjects.append(new_subject)
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ Matéria salva permanentemente no banco de dados!
                        🧠 As datas de revisão foram calculadas automaticamente.
                        🔄 Agora seus dados ficam salvos para sempre!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                    # Sugestão de próxima ação
                    st.info("💡 **Próximo passo:** Que tal usar a técnica do Palácio da Memória para fixar melhor o que acabou de estudar?")
                else:
                    st.error("❌ Erro ao salvar no banco de dados!")
    
    # Página: Minhas Matérias
    elif page == "📚 Minhas Matérias":
        st.header("📖 Suas Matérias e Cronograma de Revisões")
        
        create_weekly_calendar(st.session_state.subjects)
        
        if st.session_state.subjects:
            # Estatísticas de revisão
            col1, col2, col3 = st.columns(3)
            
            total_reviews = sum(len(s['completed_reviews']) for s in st.session_state.subjects)
            pending_reviews = 0
            today = datetime.now().date()
            
            for subject in st.session_state.subjects:
                for phase, date in subject['review_dates'].items():
                    if isinstance(date, datetime):
                        date = date.date()
                    if date <= today and phase not in subject['completed_reviews']:
                        pending_reviews += 1
            
            with col1:
                st.metric("Total de Revisões", total_reviews, "🎯")
            with col2:
                st.metric("Revisões Pendentes", pending_reviews, "📚")
            with col3:
                avg_confidence = sum(s['confidence'] for s in st.session_state.subjects) / len(st.session_state.subjects)
                st.metric("Confiança Média", f"{avg_confidence:.1f}/10", "🧠")
            
            st.subheader("📋 Lista de Matérias")
            
            for i, subject in enumerate(st.session_state.subjects):
                confidence_emoji = "🔥" if subject['confidence'] >= 8 else "💪" if subject['confidence'] >= 6 else "📚"
                
                with st.expander(f"{confidence_emoji} {subject['name']} - {subject['difficulty']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**📝 Resumo:** {subject['notes']}")
                        st.write(f"**📅 Data de Estudo:** {subject['study_date']}")
                        st.write(f"**🧠 Método Usado:** {subject['study_method']}")
                        st.write(f"**💪 Confiança:** {subject['confidence']}/10")
                        
                        if subject['reset_count'] > 0:
                            st.write(f"🔄 **Reinicializada:** {subject['reset_count']} vez(es) - Isso é normal! A persistência leva à maestria! 💪")
                    
                    with col2:
                        st.write("**📅 Próximas Revisões:**")
                        today = datetime.now().date()
                        
                        phase_names = {
                            'hoje': 'Hoje',
                            '3_dias': '3 dias',
                            '1_semana': '1 semana',
                            '1_mes': '1 mês'
                        }
                        
                        for phase, date in subject['review_dates'].items():
                            if isinstance(date, datetime):
                                date = date.date()
                            
                            status = "✅" if phase in subject['completed_reviews'] else "⏰"
                            
                            if date == today and phase not in subject['completed_reviews']:
                                st.write(f"🔥 **{phase_names[phase]}**: {date} {status}")
                            else:
                                st.write(f"{phase_names[phase]}: {date} {status}")
                    
                    # Botões de ação
                    col3, col4, col5 = st.columns(3)
                    
                    with col3:
                        if st.button(f"✅ Revisei", key=f"review_{i}"):
                            # Encontrar próxima revisão pendente
                            today = datetime.now().date()
                            for phase, date in subject['review_dates'].items():
                                if isinstance(date, datetime):
                                    date = date.date()
                                if phase not in subject['completed_reviews'] and date <= today:
                                    subject['completed_reviews'].append(phase)
                                    
                                    # Salvar no banco
                                    if save_subject(subject):
                                        # Mensagens motivacionais baseadas na fase
                                        messages = {
                                            'hoje': "🎉 Primeira revisão concluída! Você está construindo memória sólida!",
                                            '3_dias': "💪 Segunda revisão! O conhecimento está se fixando!",
                                            '1_semana': "🚀 Terceira revisão! Você está dominando este conteúdo!",
                                            '1_mes': "🏆 Revisão final! Este conhecimento agora é seu para sempre!"
                                        }
                                        
                                        st.success(messages.get(phase, "Revisão concluída!"))
                                    break
                            st.rerun()
                    
                    with col4:
                        if st.button(f"🔄 Preciso reforçar", key=f"reset_{i}"):
                            # Reiniciar o ciclo de revisões
                            subject['review_dates'] = calculate_review_dates(datetime.now())
                            subject['completed_reviews'] = []
                            subject['reset_count'] += 1
                            
                            # Salvar no banco
                            if save_subject(subject):
                                encouragements = [
                                    "💪 Não desanime! Grandes mentes também precisam de múltiplas revisões!",
                                    "🌱 Cada reinício é um novo crescimento! Você está evoluindo!",
                                    "🎯 A persistência é o que separa o bom do excelente!",
                                    "🧠 Einstein disse: 'Não é que sou muito inteligente, é que fico mais tempo com os problemas!'",
                                    "🔥 Você não está falhando, está aprendendo como aprender melhor!"
                                ]
                                
                                st.info(random.choice(encouragements))
                            st.rerun()
                    
                    with col5:
                        if st.button(f"🗑️ Remover", key=f"delete_{i}"):
                            if delete_subject(subject['id']):
                                st.session_state.subjects.pop(i)
                                st.success("Matéria removida do banco de dados!")
                            st.rerun()
        else:
            st.info("🎯 Você ainda não adicionou nenhuma matéria. Comece adicionando uma na seção 'Adicionar Matéria'!")
            
            # Dica motivacional
            st.markdown("""
            <div class="procrastination-killer">
                <h4>🚀 Dica para começar:</h4>
                <p><strong>Não espere estudar "muito" para adicionar aqui.</strong> Estudou por 15 minutos? Adicione! 
                O importante é criar o hábito de revisar. Quantidade vem com a consistência!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Página: Hábitos
    elif page == "✅ Meus Hábitos":
        st.header("🎯 Controle de Hábitos")
        
        # Estatísticas de hábitos
        if st.session_state.habits:
            today = datetime.now().date()
            habits_done_today = sum(1 for habit in st.session_state.habits if today in habit['completed_days'])
            total_habits = len(st.session_state.habits)
            
            progress_pct = (habits_done_today / total_habits) * 100 if total_habits > 0 else 0
            
            st.markdown(f"""
            <div class="streak-counter">
                📊 Progresso de Hoje: {habits_done_today}/{total_habits} hábitos ({progress_pct:.0f}%)
                {" 🔥 Você está dominando!" if progress_pct >= 80 else " 💪 Continue assim!" if progress_pct >= 50 else " 🌱 Cada passo conta!"}
            </div>
            """, unsafe_allow_html=True)
        
        # Adicionar novo hábito
        with st.expander("➕ Adicionar Novo Hábito", expanded=len(st.session_state.habits) == 0):
            st.markdown("""
            <div class="technique-card">
                <h4>💡 Dicas para hábitos que grudam:</h4>
                <ul>
                    <li><strong>Comece pequeno:</strong> "Ler 1 página" não "ler 1 hora"</li>
                    <li><strong>Seja específico:</strong> "Estudar às 19h" não "estudar à noite"</li>
                    <li><strong>Empilhe hábitos:</strong> "Depois do café, abrir o livro"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("add_habit_form"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    habit_name = st.text_input(
                        "Nome do Hábito:",
                        placeholder="Ex: Ler 15 páginas todo dia às 19h"
                    )
                    
                    habit_trigger = st.text_input(
                        "Gatilho (quando fazer?):",
                        placeholder="Ex: Logo depois do jantar"
                    )
                
                with col2:
                    habit_category = st.selectbox(
                        "Categoria:",
                        ["📚 Estudos", "🏃 Saúde", "🧘 Bem-estar", "💼 Produtividade", "🎨 Criatividade", "👨‍👩‍👧‍👦 Relacionamentos"]
                    )
                    
                    habit_difficulty = st.selectbox(
                        "Dificuldade:",
                        ["🟢 Fácil (2-5 min)", "🟡 Médio (10-20 min)", "🔴 Desafiador (30+ min)"]
                    )
                
                submitted = st.form_submit_button("➕ Adicionar Hábito")
                
                if submitted and habit_name:
                    new_habit = {
                        'name': habit_name,
                        'trigger': habit_trigger,
                        'category': habit_category,
                        'difficulty': habit_difficulty,
                        'created_date': datetime.now().date(),
                        'completed_days': [],
                        'best_streak': 0
                    }
                    
                    # Salvar no banco
                    if save_habit(new_habit):
                        st.session_state.habits.append(new_habit)
                        st.success("🎉 Hábito salvo permanentemente! Lembre-se: consistência é mais importante que perfeição!")
                    st.rerun()
        
        # Lista de hábitos
        if st.session_state.habits:
            st.subheader("📋 Seus Hábitos")
            
            today = datetime.now().date()
            
            for i, habit in enumerate(st.session_state.habits):
                # Calcular streak atual
                current_streak = 0
                check_date = today
                while check_date in habit['completed_days']:
                    current_streak += 1
                    check_date -= timedelta(days=1)
                
                # Atualizar melhor streak
                if current_streak > habit.get('best_streak', 0):
                    habit['best_streak'] = current_streak
                    save_habit(habit)  # Salvar no banco
                
                streak_emoji = "🔥" if current_streak >= 7 else "⭐" if current_streak >= 3 else "🌱"
                
                with st.container():
                    st.markdown(f"""
                    <div class="habit-card">
                        <h4>{habit['category']} {habit['name']}</h4>
                        <p><strong>Gatilho:</strong> {habit.get('trigger', 'Não definido')} | 
                        <strong>Dificuldade:</strong> {habit['difficulty']}</p>
                        <p>Criado em: {habit['created_date']} | 
                        Streak atual: {streak_emoji} {current_streak} dias | 
                        Recorde: 🏆 {habit.get('best_streak', 0)} dias</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        # Mostrar últimos 14 dias
                        last_14_days = [today - timedelta(days=x) for x in range(13, -1, -1)]
                        day_status = ""
                        for day in last_14_days:
                            if day in habit['completed_days']:
                                day_status += "✅"
                            else:
                                day_status += "⭕"
                        st.write(f"Últimos 14 dias: {day_status}")
                    
                    with col2:
                        if today not in habit['completed_days']:
                            if st.button(f"✅ Feito!", key=f"complete_habit_{i}"):
                                habit['completed_days'].append(today)
                                
                                # Salvar no banco
                                if save_habit(habit):
                                    # Mensagens motivacionais baseadas no streak
                                    if current_streak + 1 == 1:
                                        st.success("🎉 Primeiro dia! Todo grande hábito começa com um passo!")
                                    elif current_streak + 1 == 3:
                                        st.success("⭐ 3 dias seguidos! O hábito está se formando!")
                                    elif current_streak + 1 == 7:
                                        st.success("🔥 Uma semana! Você está pegando fogo!")
                                    elif current_streak + 1 == 30:
                                        st.success("🚀 Um mês! Esse hábito agora é parte de quem você é!")
                                    else:
                                        st.success(f"💪 Mais um dia conquistado! Streak: {current_streak + 1}")
                                
                                st.rerun()
                        else:
                            st.success("✅ Feito!")
                    
                    with col3:
                        if today in habit['completed_days']:
                            if st.button(f"↩️ Desfazer", key=f"undo_habit_{i}"):
                                habit['completed_days'].remove(today)
                                if save_habit(habit):
                                    st.info("Desfeito! Não se preocupe, todos temos dias difíceis.")
                                st.rerun()
                    
                    with col4:
                        if st.button(f"🗑️ Remover", key=f"delete_habit_{i}"):
                            if delete_habit(habit['id']):
                                st.session_state.habits.pop(i)
                                st.success("Hábito removido do banco de dados!")
                            st.rerun()
                    
                    # Dicas baseadas no progresso
                    if current_streak == 0 and len(habit['completed_days']) > 0:
                        st.warning("💡 **Dica:** Quebrou o streak? Normal! O importante é recomeçar hoje. Progressão não é perfeição!")
                    elif current_streak >= 21:
                        st.success("🏆 **Parabéns!** Cientificamente, você já formou este hábito! Agora é automático!")
        
        else:
            st.info("🎯 Você ainda não tem hábitos cadastrados. Adicione um acima!")
            
            # Sugestões de hábitos
            st.markdown("""
            <div class="procrastination-killer">
                <h4>💡 Sugestões de Hábitos Poderosos:</h4>
                <ul>
                    <li>📚 <strong>Estudar 25 min todo dia às 19h</strong> (depois do jantar)</li>
                    <li>🧠 <strong>Revisar flashcards 10 min no transporte</strong></li>
                    <li>📝 <strong>Escrever 3 coisas que aprendi hoje</strong> (antes de dormir)</li>
                    <li>🏃 <strong>Caminhar 15 min</strong> (depois do almoço)</li>
                    <li>🧘 <strong>Meditar 5 min</strong> (logo ao acordar)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #42A5F5; font-style: italic;">
        💙 StudyFlow Pro - Transformando procrastinação em conquistas diárias
        <br>🧠 "A diferença entre o ordinário e o extraordinário é a prática deliberada"
        <br>🔒 Seus dados ficam salvos permanentemente no Supabase
        <br>🔑 Sistema de código pessoal - acesse de qualquer dispositivo!
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
