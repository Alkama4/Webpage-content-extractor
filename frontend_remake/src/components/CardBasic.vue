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
}

.header {
    color: var(--text-dark-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--fs-4);
    font-weight: var(--fw-bold);
    margin-bottom: 4px;
}
.header i {
    font-size: var(--fs-5);
    color: var(--color-primary-500);
    transition: color var(--t-fast);
}
.card:hover .header i {
    color: var(--color-primary-600);
}
.desc {
    color: var(--text-dark-secondary);
    font-size: var(--fs-2);
    line-height: 1.5;
    margin-bottom: 1.5rem;
}

.header-row {
    margin-bottom: 1rem;
}

</style>