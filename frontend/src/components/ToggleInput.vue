<template>
    <div class="toggle-input" @click="toggleModelValue">
        <label :for="id">{{ label }}</label>
        <div
            class="switch"
            :class="{ active: !!modelValue }"
            tabindex="0"
            @keydown.space.prevent="toggleModelValue"
            @keydown.enter.prevent="toggleModelValue"
        >
            <div class="slider"></div>
        </div>
    </div>
</template>

<script lang="ts">
export default {
    name: 'ToggleInput',
    props: {
        modelValue: { type: Boolean, required: true },
        label:      { type: String,  default: '' },
        placeholder:{ type: String,  default: '' },
        id: {
            type: String,
            default: () => `input-${Math.random().toString(36).substr(2, 9)}`,
        },
    },
    emits: ['update:modelValue'],

    methods: {
        toggleModelValue() {
            const newVal = !this.modelValue;          // invert current value
            this.$emit('update:modelValue', newVal);   // send to parent
        },
    },
};
</script>



<style scoped>
.toggle-input {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin: 12px 0;
}
label {
    font-size: var(--fs-2);
}

.switch {
    --sw-height: 28px;
    --gap: 4px;
    --slider-multiplayer: 2.25;
    --border-width: 0px;
    
    --sl-height: calc(1 * var(--sw-height) - 2 * (var(--gap)));
    --sw-width: calc(var(--slider-multiplayer) * var(--sl-height) + 2 * (var(--gap) + var(--border-width)));

    height: var(--sw-height);
    width: var(--sw-width);
    border: var(--border-width) solid var(--color-neutral-300);
    border-radius: 100px;
    background-color: var(--color-neutral-300);
    cursor: pointer;
    position: relative;
    transition: border-color var(--t-fast),
                background-color var(--t-fast);
}
.switch:hover {
    border-color: var(--color-neutral-400);
    background-color: var(--color-neutral-400);
}
.switch.active {
    background-color: var(--color-primary-500);
}
.switch.active:hover {
    background-color: var(--color-primary-600);
}

.slider {
    position: absolute;
    left: var(--gap);
    top: var(--gap);
    bottom: var(--gap);
    width: var(--sl-height);

    background-color: var(--color-neutral-50);
    border-radius: 100px;
    transition: left var(--t-fast);
}

.switch.active .slider {
    left: calc(var(--sw-width) - var(--sl-height) - var(--gap));
}
</style>