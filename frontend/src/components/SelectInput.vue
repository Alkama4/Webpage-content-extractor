<template>
    <div class="select-input">
        <label :for="id">{{ label }}</label>
        <div :class="['rel-wrapper', { open: isOpen }]">
            <select
                :value="modelValue"
                :disabled="disabled"
                @change="$emit('update:modelValue', $event.target.value)"
            >
                <option v-for="option in options" :key="option.value" :value="option.value">
                    {{ option.label }}
                </option>
            </select>
            <i class="bx bx-chevron-down"></i>
        </div>
    </div>
</template>

<script>
export default {
    name: "SelectInput",
    data() {
        return {
            isOpen: false,
            isFocus: false
        }
    },
    props: {
        modelValue: String,
        label: String,
        options: {
            type: Array,
            default: () => []
        },
        id: {
            type: String,
            default: () => `select-${Math.random().toString(36).substr(2, 9)}`
        },
        disabled: {
            type: Boolean,
            default: false
        }
    },
    emits: ["update:modelValue"]
}
</script>

<style scoped>
.select-input {
    display: flex;
    flex-direction: column;
}
label {
    font-size: var(--fs-1);
}

select {
    appearance:none;
    width: 100%;
}

.rel-wrapper {
    position: relative;
}

i {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;

    font-size: var(--fs-6);
    color: var(--text-dark-secondary);
}

</style>
