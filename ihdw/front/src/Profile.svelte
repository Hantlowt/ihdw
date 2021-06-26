<script>
	import { afterUpdate } from 'svelte';
	export let api;
	let informations;
	let new_name=''
	let new_password=''
	let message;
	$: informations = api ? api.getProfileInformations() : null;
	async function updateProfile() {
		message = api.updateProfile(new_name, new_password)
	}
</script>

<aside>
{#if informations}
	{#await informations}
	Loading...
	{:then profile}
	<h1>Update profile</h1>
	New Name: <input autocomplete="fuck" type="text" bind:value={new_name} placeholder="{profile.name}" />
	New Password: <input autocomplete="fuck" type="password" bind:value={new_password} />
	<button on:click={updateProfile}>Update</button>
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