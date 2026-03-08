<script setup lang="ts">
import { ref, onMounted } from "vue";
import { invoke } from "@tauri-apps/api/core";

const wakeWord = ref("hey_jarvis");
const ttsEngine = ref("piper");
const sttModel = ref("tiny");
const sandboxMode = ref(true);
const isListening = ref(true);

interface SkillInfo {
  name: string;
  icon: string;
  description: string;
  dangerous: boolean;
  enabled: boolean;
}

const skills = ref<SkillInfo[]>([
  {
    name: "App Launcher",
    icon: "🚀",
    description: "Open and close applications",
    dangerous: false,
    enabled: true,
  },
  {
    name: "File Manager",
    icon: "📁",
    description: "Read, write, and create files",
    dangerous: true,
    enabled: true,
  },
  {
    name: "Browser",
    icon: "🌐",
    description: "Open URLs and search the web",
    dangerous: true,
    enabled: true,
  },
  {
    name: "Shell",
    icon: "⌨️",
    description: "Execute terminal commands",
    dangerous: true,
    enabled: true,
  },
  {
    name: "Dictation",
    icon: "✍️",
    description: "Auto-type text anywhere",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Screenshot",
    icon: "📸",
    description: "Capture the screen",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Calendar",
    icon: "📅",
    description: "Date and time information",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Email Draft",
    icon: "✉️",
    description: "Compose email drafts",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Notifications",
    icon: "🔔",
    description: "System notifications",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Web Search",
    icon: "🔍",
    description: "Answer questions and search",
    dangerous: false,
    enabled: true,
  },
]);

async function updateWakeWord() {
  try {
    await invoke("set_wake_word", { word: wakeWord.value });
  } catch (e) {
    console.error(e);
  }
}

async function updateTtsEngine() {
  try {
    await invoke("set_tts_engine", { engine: ttsEngine.value });
  } catch (e) {
    console.error(e);
  }
}

async function updateSandbox() {
  try {
    await invoke("set_sandbox_mode", { enabled: sandboxMode.value });
  } catch (e) {
    console.error(e);
  }
}

onMounted(async () => {
  try {
    const status = await invoke<{ status: string; listening: boolean }>(
      "get_engine_status",
    );
    isListening.value = status.listening;
  } catch (e) {
    console.error(e);
  }
});
</script>

<template>
  <div class="titlebar">VOICESAFECLAW</div>
  <div class="app-container">
    <!-- Status -->
    <div class="status-banner">
      <div
        class="status-dot"
        :style="{ background: isListening ? '#34d399' : '#f87171' }"
      ></div>
      <span class="status-text">{{
        isListening ? "Listening" : "Paused"
      }}</span>
      <span class="status-sub">v1.0.0 · Local Mode</span>
    </div>

    <!-- Voice Settings -->
    <div class="settings-card">
      <div class="card-title">🎙️ Voice Settings</div>

      <div class="setting-row">
        <div>
          <div class="setting-label">Wake Word</div>
          <div class="setting-desc">Trigger phrase to activate Jarvis</div>
        </div>
        <input type="text" v-model="wakeWord" @change="updateWakeWord" />
      </div>

      <div class="setting-row">
        <div>
          <div class="setting-label">TTS Engine</div>
          <div class="setting-desc">Voice synthesis engine</div>
        </div>
        <select v-model="ttsEngine" @change="updateTtsEngine">
          <option value="piper">Piper TTS</option>
          <option value="kokoro">Kokoro ONNX</option>
          <option value="system">System Default</option>
        </select>
      </div>

      <div class="setting-row">
        <div>
          <div class="setting-label">STT Model</div>
          <div class="setting-desc">Speech recognition accuracy vs speed</div>
        </div>
        <select v-model="sttModel">
          <option value="tiny">Tiny (fastest)</option>
          <option value="base">Base (balanced)</option>
          <option value="small">Small (most accurate)</option>
        </select>
      </div>
    </div>

    <!-- Security -->
    <div class="settings-card">
      <div class="card-title">🛡️ Security</div>
      <div class="setting-row">
        <div>
          <div class="setting-label">Sandbox Mode</div>
          <div class="setting-desc">Require approval for all actions</div>
        </div>
        <label class="toggle">
          <input
            type="checkbox"
            v-model="sandboxMode"
            @change="updateSandbox"
          />
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>

    <!-- Skills -->
    <div class="settings-card">
      <div class="card-title">⚡ Skills</div>
      <div v-for="skill in skills" :key="skill.name" class="skill-item">
        <div class="skill-icon">{{ skill.icon }}</div>
        <div class="skill-info">
          <div class="skill-name">{{ skill.name }}</div>
          <div class="skill-desc">{{ skill.description }}</div>
        </div>
        <span v-if="skill.dangerous" class="skill-badge badge-danger"
          >⚠ Approval</span
        >
        <label class="toggle">
          <input type="checkbox" v-model="skill.enabled" />
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>
  </div>
</template>
