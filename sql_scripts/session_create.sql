create function make_session(username, interface, end_date) returns trigger as $make_session$
  begin
    -- find the previous corresponding connect_log entry
    select * into conn_start from connect_log
    where username=username and interface=interface and created_at < 

    -- create a record in the session table consisting of this info + when the session started
    insert into sessions (username, interface, local_ip, remote_ip, started_at, ended_at)
    
    -- FIXME: associate all access_log entries for this user in this duration w/the session?
  end;
$make_session$ LANGUAGE plpgsql;

create trigger make_session
  after insert
  on connect_log
  when (new.status == 'disconnected')
  execute procedure make_session(new.username, new.interface, new.created_at);

