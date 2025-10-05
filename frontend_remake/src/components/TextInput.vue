<template>
    <div class="text-input">
        <label :for="id">{{ label }}</label>
        <input
            :id="id"
            type="text"
            :value="modelValue"
            :placeholder="placeholder"
            @input="$emit('update:modelValue', $event.target.value)"
        >
    </div>
</template>

<script>
export default {
    name: "TextInput",
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
.text-input {
    display: flex;
    flex-direction: column;
}
label {
    font-size: var(--fs-1);
}
</style>