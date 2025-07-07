<template>
  <div class="chat-container">
    <h1>🤖 Asistente de Programación</h1>
    <div class="chat-window" ref="chatWindow">
      <transition-group name="fade" tag="div">
        <div
          v-for="(msg, index) in mensajes"
          :key="index"
          :class="['mensaje', msg.tipo]"
        >
          <img
            class="avatar"
            :src="msg.tipo === 'bot' ? botAvatar : userAvatar"
            alt="avatar"
          />
          <span class="texto">{{ msg.texto }}</span>
        </div>
        <div v-if="cargando" key="typing" class="mensaje bot typing">
          <img class="avatar" :src="botAvatar" alt="avatar" />
          <span class="texto typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </span>
        </div>
      </transition-group>
    </div>
    <form class="input-area" @submit.prevent="enviarPregunta">
      <input
        v-model="query"
        :disabled="cargando"
        placeholder="Escribe tu mensaje..."
      />
      <button type="submit" :disabled="cargando">
        {{ cargando ? 'Esperando...' : 'Enviar' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import axios from 'axios'

const query = ref('')
const mensajes = ref([])
const cargando = ref(false)
const chatWindow = ref(null)

const botAvatar = 'https://cdn-icons-png.flaticon.com/512/4712/4712109.png'
const userAvatar = 'https://cdn-icons-png.flaticon.com/512/4712/4712105.png'

// Cargar historial desde localStorage
onMounted(() => {
  const guardado = localStorage.getItem('chat_historial')
  if (guardado) {
    mensajes.value = JSON.parse(guardado)
    nextTick(scrollToBottom)
  }
})

// Guardar historial cada vez que cambia
watch(mensajes, (nuevo) => {
  localStorage.setItem('chat_historial', JSON.stringify(nuevo))
}, { deep: true })

const enviarPregunta = async () => {
  if (!query.value.trim() || cargando.value) return

  cargando.value = true
  mensajes.value.push({ texto: query.value, tipo: 'usuario' })

  await nextTick()
  scrollToBottom()

  try {
    const res = await axios.post(
      'http://localhost:8000/response',
      { query: query.value },
      {
        headers: { 'x-api-key': 'miclaveultrasecreta' },
        timeout: 60000
      }
    )
    mensajes.value.push({ texto: res.data.response, tipo: 'bot' })
  } catch (error) {
    const errorMsg = error.code === 'ECONNABORTED'
      ? '⏱️ Tiempo de espera agotado'
      : '❌ Error al obtener respuesta'
    mensajes.value.push({ texto: errorMsg, tipo: 'bot' })
  }

  query.value = ''
  cargando.value = false
  await nextTick()
  scrollToBottom()
}

const scrollToBottom = () => {
  if (chatWindow.value) {
    chatWindow.value.scrollTop = chatWindow.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 600px;
  margin: 2rem auto;
  font-family: sans-serif;
  display: flex;
  flex-direction: column;
  height: 90vh;
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
}

h1 {
  text-align: center;
  margin: 1rem 0;
}

.chat-window {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background-color: midnightblue;
  display: flex;
  flex-direction: column;
}

.mensaje {
  display: flex;
  align-items: flex-start;
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  line-height: 1.4;
  word-wrap: break-word;
  transition: all 0.3s ease;
}

.usuario {
  align-self: flex-end;
  background-color: #d1e7dd96;
  color: #0f5132;
  flex-direction: row-reverse;
}

.bot {
  align-self: flex-start;
  background-color: #e2e3e5;
  color: #41464b;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin: 0 0.5rem;
}

.texto {
  flex: 1;
}

/* Espaciado entre mensajes */
.mensaje + .mensaje {
  margin-top: 0.25rem;
}

.mensaje.usuario + .mensaje.bot,
.mensaje.bot + .mensaje.usuario {
  margin-top: 1.25rem;
}

.input-area {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #ccc;
  background:  f9f9f9;
}

input {
  flex: 1;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  margin-left: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  background-color: rgba(24, 24, 96, 0.715);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0b5ed7;
}

/* Animación de entrada */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Indicador de escritura */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 1.5rem;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #555;
  border-radius: 50%;
  animation: blink 1.4s infinite both;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0% {
    opacity: 0.2;
    transform: scale(1);
  }
  20% {
    opacity: 1;
    transform: scale(1.3);
  }
  100% {
    opacity: 0.2;
    transform: scale(1);
  }
}
</style>