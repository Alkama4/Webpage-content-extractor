<template>
    <div class="card-basic card">
        <div class="header-row">
            <div class="header">
                <i class="bx" :class="icon"></i>
                <span>{{ title }}</span>
            </div>
            <div class="desc">{{ description }}</div>
        </div>
        <slot></slot>
    </div>
</template>

<script>
export default {
  name: 'CardBasic',
  props: {
    title: { type: String, default: 'Untitled' },
    description: { type: String, default: 'Untitled' },
    icon: { type: String, default: 'bxs-grid' }
  }
}
</script>

<style scoped>
.card {
    display: flex;
    flex-direction: column;
    background-color: var(--color-neutral-100);
}

.header {
    color: var(--text-dark-primary);
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: var(--fs-3);
    font-weight: var(--fw-semibold);
}
.header i {
    font-size: var(--fs-5);
    color: var(--color-primary-500);
}
.desc {
    color: var(--text-dark-secondary);
    font-size: var(--fs-1);
}

.header-row {
    margin-bottom: 1rem;
}

</style>