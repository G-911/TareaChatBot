<template>
  <div class="container">
    <h1>🤖 Asistente de Programación</h1>
    <form @submit.prevent="enviarPregunta">
      <input v-model="query" placeholder="Escribe tu pregunta..." />
      <button type="submit">Enviar</button>
    </form>
    <div v-if="respuesta" class="respuesta">
      <strong>Respuesta:</strong> {{ respuesta }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const query = ref('')
const respuesta = ref('')

const enviarPregunta = async () => {
  try {
    const res = await axios.post(
      'http://localhost:8000',
      { query: query.value },
      { headers: { 'x-api-key': import.meta.env.VITE_API_KEY } }
    )
    respuesta.value = res.data.response
  } catch (error) {
    respuesta.value = '❌ Error al obtener respuesta'
    console.error(error)
  }
}
</script>

<style>
.container {
  max-width: 600px;
  margin: 2rem auto;
  font-family: sans-serif;
}
input {
  width: 80%;
  padding: 0.5rem;
}
button {
  padding: 0.5rem 1rem;
}
.respuesta {
  margin-top: 1rem;
  background: #f0f0f0;
  padding: 1rem;
}
</style>