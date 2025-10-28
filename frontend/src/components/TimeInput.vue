<template>
    <div class="time-input">
        <label :for="id">{{ label }}</label>
        <input
            :id="id"
            type="time"
            :value="modelValue"
            :placeholder="placeholder"
            @input="$emit('update:modelValue', $event.target.value)"
        >
    </div>
</template>

<script>
export default {
    name: "TimeInput",
    props: {
        modelValue: String,
        label: String,
        placeholder: String,
        id: {
            type: String,
            default: () => `input-${Math.random().toString(36).substr(2, 9)}`
        }
    },
    emits: ["update:modelValue"]
}
</script>


<style scoped>
.time-input {
    display: flex;
    flex-direction: column;
}
label {
    font-size: var(--fs-1);
}
</style>