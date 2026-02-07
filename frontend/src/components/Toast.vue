<template>
    <div class="toast-container">
        <transition-group name="toast-fade">
            <div v-for="toast in toasts" :key="toast.id" class="toast-item">
                <span>{{ toast.message }}</span>
                <i 
                    class="bx bx-x"
                    @click="removeToast(toast.id)"
                ></i>
            </div>
        </transition-group>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const toasts = ref([]);

const removeToast = (id) => {
    toasts.value = toasts.value.filter(t => t.id !== id);
};

const addToast = (event) => {
    const id = Date.now();
    toasts.value.push({ id, message: event.detail });
    
    setTimeout(() => {
        removeToast(id);
    }, 5000);
};

onMounted(() => window.addEventListener('notify', addToast));
onUnmounted(() => window.removeEventListener('notify', addToast));
</script>

<style scoped>
.toast-container {
    position: fixed;
    bottom: 32px;
    left: 0;
    width: 100vw;
    display: flex;
    align-items: center;
    flex-direction: column-reverse;
    gap: 10px;
    z-index: 9999;
    pointer-events: none;
}

.toast-item {
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;

    background: var(--color-error);
    color: var(--text-light-primary);
    box-shadow: var(--shadow-md);

    padding: 12px 24px;
    border-radius: 8px;
    pointer-events: auto;
    min-width: 200px;
}

.toast-fade-move {
  transition: transform 0.3s ease;
}
.toast-fade-leave-active {
  position: absolute;
  transition: all 0.3s ease;
}
.toast-fade-enter-active {
  transition: all 0.3s ease;
}
.toast-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.toast-fade-leave-to {
  opacity: 0;
  transform: scale(0.9); 
}

i {
    font-size: var(--fs-4);
    transition: background-color var(--t-fast);
    border-radius: 100px;
    padding: 4px;
    cursor: pointer;
}
i:hover {
    background-color: #ffffff34;
}
</style>