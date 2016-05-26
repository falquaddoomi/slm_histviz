-- noinspection SqlResolveForFile

create or replace function make_session() returns trigger as $body$
  declare
    conn_start timestamp without time zone;
  begin
    -- find the previous corresponding connect_log entry
    select created_at into conn_start from connect_log
    where username=new.username and interface=new.interface
          and status='connected' and created_at < new.created_at
    order by created_at desc limit 1;

    -- create a record in the session table consisting of this info + when the session started
    insert into sessions (username, interface, local_ip, remote_ip, started_at, ended_at)
    values (new.username, new.interface, new.local_ip, new.remote_ip, conn_start, new.created_at);
    
    -- FIXME: associate all access_log entries for this user in this duration w/the session?
    return null;
  end;
$body$ LANGUAGE 'plpgsql' SECURITY DEFINER;

drop trigger if exists make_session on connect_log;
create trigger make_session
  after insert
  on connect_log
  for each row
  when (new.status='disconnected')
  execute procedure make_session();
