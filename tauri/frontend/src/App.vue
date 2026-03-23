<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
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
    description: "Launch desktop applications instantly",
    dangerous: false,
    enabled: true,
  },
  {
    name: "File Manager",
    icon: "📁",
    description: "File system traversal and operations",
    dangerous: true,
    enabled: true,
  },
  {
    name: "Browser",
    icon: "🌐",
    description: "Automate web browsing and search",
    dangerous: true,
    enabled: true,
  },
  {
    name: "Shell",
    icon: "⌨️",
    description: "Execute raw terminal system commands",
    dangerous: true,
    enabled: true,
  },
  {
    name: "Dictation",
    icon: "✍️",
    description: "Deep integrated auto-typing globally",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Screenshot",
    icon: "📸",
    description: "Capture visible display buffers",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Calendar",
    icon: "📅",
    description: "Schedule & timeline synchronization",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Email Draft",
    icon: "✉️",
    description: "Composes outbound communications",
    dangerous: false,
    enabled: true,
  },
  {
    name: "Web Search",
    icon: "🔍",
    description: "Real-time indexed semantic search",
    dangerous: false,
    enabled: true,
  },
  {
    name: "System Auth",
    icon: "🔐",
    description: "Manage encrypted credentials",
    dangerous: true,
    enabled: true,
  },
]);

const quickActions = computed(() => skills.value.slice(0, 4));
const otherSkills = computed(() => skills.value.slice(4));

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

function toggleSkill(skill: SkillInfo) {
  skill.enabled = !skill.enabled;
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
  <!-- Background Effects -->
  <div class="app-background">
    <div class="bg-glow teal-glow"></div>
    <div class="bg-glow violet-glow"></div>
    <div class="bg-glow cyan-glow"></div>
    <div class="grain"></div>
  </div>

  <div class="titlebar">VOICESAFECLAW CORE</div>
  
  <div class="app-container">
    
    <!-- Hero Section -->
    <header class="hero-section">
      <div class="ai-orb">
        <div class="orb-core"></div>
        <div class="orb-ring ring-1"></div>
        <div class="orb-ring ring-2"></div>
      </div>
      <div class="hero-content">
        <div class="status-badge" :class="{ active: isListening }">
          <div class="status-dot"></div>
          <span>{{ isListening ? "READY FOR COMMAND" : "SYSTEM PAUSED" }}</span>
        </div>
        <h1 class="greeting">Good evening, Pranshu. All systems operational.</h1>
      </div>
    </header>

    <!-- Quick Action Cards -->
    <section class="quick-actions">
      <div class="action-card" v-for="action in quickActions" :key="action.name" @click="toggleSkill(action)" :class="{ active: action.enabled }">
        <div class="action-icon">{{ action.icon }}</div>
        <div class="action-label">{{ action.name }}</div>
        <div class="action-status" v-if="action.enabled"></div>
      </div>
    </section>

    <div class="dashboard-grid">
      <!-- Settings Column -->
      <div class="column-settings">
        <h2 class="section-title">System Configuration</h2>
        
        <details class="glass-panel" open>
          <summary>
            <div class="panel-header">
              <span class="panel-icon">🎙️</span> Voice Interface
            </div>
            <div class="chevron"></div>
          </summary>
          <div class="panel-content">
            <div class="setting-row">
              <div class="setting-info">
                <label>Wake Word</label>
                <span>Trigger phrase to activate AI</span>
              </div>
              <input type="text" class="cyber-input" v-model="wakeWord" @change="updateWakeWord" />
            </div>

            <div class="setting-row">
              <div class="setting-info">
                <label>Vocal Synthesis</label>
                <span>TTS Engine</span>
              </div>
              <div class="cyber-select-wrapper">
                <select class="cyber-select" v-model="ttsEngine" @change="updateTtsEngine">
                  <option value="piper">Piper Neural</option>
                  <option value="kokoro">Kokoro ONNX</option>
                  <option value="system">Native OS API</option>
                </select>
              </div>
            </div>

            <div class="setting-row">
              <div class="setting-info">
                <label>Recognition Model</label>
                <span>STT Accuracy Configuration</span>
              </div>
              <div class="cyber-select-wrapper">
                <select class="cyber-select" v-model="sttModel">
                  <option value="tiny">Tiny (Ultra-fast)</option>
                  <option value="base">Base (Balanced)</option>
                  <option value="small">Small (Precision)</option>
                </select>
              </div>
            </div>
          </div>
        </details>

        <details class="glass-panel" open>
          <summary>
            <div class="panel-header">
              <span class="panel-icon">🛡️</span> Security Protocols
            </div>
            <div class="chevron"></div>
          </summary>
          <div class="panel-content">
            <div class="setting-row">
              <div class="setting-info">
                <label>Strict Sandbox</label>
                <span>Require manual override for all actions</span>
              </div>
              <label class="cyber-toggle">
                <input type="checkbox" v-model="sandboxMode" @change="updateSandbox" />
                <div class="toggle-track">
                  <div class="toggle-thumb"></div>
                </div>
              </label>
            </div>
          </div>
        </details>
      </div>

      <!-- Skills Column -->
      <div class="column-skills">
        <h2 class="section-title">Active Capabilities</h2>
        <div class="skills-grid">
          <div 
            class="skill-card" 
            v-for="skill in otherSkills" 
            :key="skill.name" 
            :class="{ active: skill.enabled }"
          >
            <div class="card-header">
              <div class="skill-icon-wrap">{{ skill.icon }}</div>
              <label class="cyber-toggle small violet">
                <input type="checkbox" v-model="skill.enabled" />
                <div class="toggle-track">
                  <div class="toggle-thumb"></div>
                </div>
              </label>
            </div>
            <div class="skill-content">
              <h3>{{ skill.name }}</h3>
              <p>{{ skill.description }}</p>
            </div>
            <div class="skill-footer" v-if="skill.dangerous">
              <span class="danger-badge">RESTRICTED API</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
