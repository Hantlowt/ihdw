<script>
    import Loading from  './Loading.svelte'
    export let api;
    export let category;
    export let id;

    let contentPromise;

    $: if (api) contentPromise = api.getContent(id, category)
</script>

<aside>
{#await contentPromise}
    <Loading enabled=true />
{:then data}
    {#each Object.keys(data) as key}
    <details>
        <summary>{key}</summary>
        <p>{data[key].content}</p>
    </details>
    {/each}
{/await}
</aside>