<script>
	import { afterUpdate } from 'svelte';
	export let api;
	let informations;
	let new_name='';
	let new_url='';
	let message;
	$: informations = api ? api.getConfig() : null;
	async function updateConfig() {
		message = api.updateConfig(new_name, new_url)
	}
</script>
<section>
<aside>
{#if informations}
	{#await informations}
	Loading...
	{:then config}
	<h1>Update global config</h1>
	Website name: <input type="text" bind:value={new_name} placeholder="{config.name}" />
	Website URL: <input type="text" bind:value={new_url} placeholder="{config.url}"/>
	<button on:click={updateConfig}>Update</button>
	{#if message}
		{#await message}
		{:then m}
		<p>{m}</p>
		{:catch m}
		<p style='color: red;'>{m}</p>
		{/await}
	{/if}
	{:catch}
	Oups...
	{/await}
{/if}
</aside>
</section>