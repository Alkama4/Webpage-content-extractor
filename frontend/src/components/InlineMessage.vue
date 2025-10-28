<template>
    <div 
        class="inline-message space-between vertical-align"
        :class="[ type, { interaction } ]"
        @click="close"
    >
        <span>{{ text }}</span>
        <i class="bx bx-x" v-if="interaction"></i>
    </div>
</template>

<script>
export default {
    name: 'InlineMessage',
    props: {
        text: { type: String },
        type: { type: String, default: 'error'},
        interaction: { type: Boolean, default: true }
    },
    emits: ['close'],
    methods: {
        close() {
            this.$emit('close');
        }
    }
}
</script>

<style scoped>
.inline-message {
    padding: 4px 12px;
    border-radius: 8px;
    box-sizing: border-box;
    transition: var(--t-fast) background-color;
    font-size: var(--fs-1);
}
.inline-message.interaction {
    cursor: pointer;
}

.inline-message.error {
    background-color: var(--color-error);
    color: var(--text-light-primary);
}
.inline-message.error.interaction:hover {
    background-color: var(--color-error-light);
}

.inline-message.warning {
    background-color: var(--color-warning);
    color: var(--text-light-primary);
}
.inline-message.warning.interaction:hover {
    background-color: var(--color-warning-hover);
}


i {
    font-size: var(--fs-4);
    transition: background-color var(--t-fast);
    border-radius: 100px;
    padding: 4px;
}
i:hover {
    background-color: #ffffff34;
}
</style>