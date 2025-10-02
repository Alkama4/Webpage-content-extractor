<template>
    <div class="listing-placeholder">
        <i class="bx" :class="icon"></i>
        <div class="text">{{ text }}</div>
        <div class="desc">{{ desc }}</div>
    </div>
</template>

<script>
export default {
    props: {
        icon: { type: String, default: 'bxs-error' },
        text: { type: String, default: 'Placeholder' },
        desc: { type: String, default: 'Placeholder description' },
    }
}
</script>

<style scoped>
.listing-placeholder {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border: 2px dashed var(--color-neutral-300);
    border-radius: var(--card-radius);
    height: 100%;
    width: 100%;
    padding: 1rem;
    box-sizing: border-box;

    color: var(--text-dark-tertiary);
}

i {
    color: var(--color-primary-400);
    font-size: var(--fs-6);
    margin-bottom: 1rem;
}

.text {
    font-size: var(--fs-1);
}

.desc {
    text-align: center;
    font-size: var(--fs-0);
}
</style>